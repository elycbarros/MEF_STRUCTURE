use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RustHole {
    pub x_min: f64,
    pub y_min: f64,
    pub x_max: f64,
    pub y_max: f64,
}

#[pymethods]
impl RustHole {
    #[new]
    pub fn new(x_min: f64, y_min: f64, x_max: f64, y_max: f64) -> Self {
        Self { x_min, y_min, x_max, y_max }
    }

    pub fn contains(&self, x: f64, y: f64) -> bool {
        let eps = 1e-9;
        x >= self.x_min - eps && x <= self.x_max + eps &&
        y >= self.y_min - eps && y <= self.y_max + eps
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RustPillar {
    pub id: String,
    pub x: f64,
    pub y: f64,
    pub p_kn: f64,
    pub bx: f64,
    pub by: f64,
}

#[pymethods]
impl RustPillar {
    #[new]
    pub fn new(id: String, x: f64, y: f64, p_kn: f64, bx: f64, by: f64) -> Self {
        Self { id, x, y, p_kn, bx, by }
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SlabModel {
    pub lx: f64,
    pub ly: f64,
    pub nx: usize,
    pub ny: usize,
    pub holes: Vec<RustHole>,
    pub pillars: Vec<RustPillar>,
    pub q_total: f64, // Area load in N/m2
}

#[pymethods]
impl SlabModel {
    #[new]
    pub fn new(lx: f64, ly: f64, nx: usize, ny: usize, holes: Vec<RustHole>, pillars: Vec<RustPillar>, q_total: f64) -> Self {
        Self { lx, ly, nx, ny, holes, pillars, q_total }
    }
}

pub struct SlabMesh {
    pub nodes: Vec<(f64, f64)>,
    pub elements: Vec<[usize; 4]>,
    pub support_nodes: Vec<usize>,
    pub nodal_loads: Vec<f64>, // w-load at each node (N)
}

pub fn generate_mesh(model: &SlabModel) -> SlabMesh {
    let mut nodes = Vec::new();
    let dx = model.lx / (model.nx - 1) as f64;
    let dy = model.ly / (model.ny - 1) as f64;
    let n_nodes = model.nx * model.ny;

    for j in 0..model.ny {
        for i in 0..model.nx {
            nodes.push((i as f64 * dx, j as f64 * dy));
        }
    }

    let mut nodal_loads = vec![0.0; n_nodes];
    let mut elements = Vec::new();
    let area_per_node = (dx * dy) / 4.0; // Simplificado: area do elemento dividida por 4

    for j in 0..(model.ny - 1) {
        for i in 0..(model.nx - 1) {
            let n0 = j * model.nx + i;
            let n1 = n0 + 1;
            let n2 = n0 + model.nx + 1;
            let n3 = n0 + model.nx;

            let ex = (nodes[n0].0 + nodes[n2].0) / 2.0;
            let ey = (nodes[n0].1 + nodes[n2].1) / 2.0;

            let mut skip = false;
            for hole in &model.holes {
                if hole.contains(ex, ey) {
                    skip = true;
                    break;
                }
            }

            if !skip {
                elements.push([n0, n1, n2, n3]);
                // Adicionar carga de área
                let load_val = model.q_total * (dx * dy) / 4.0;
                nodal_loads[n0] += load_val;
                nodal_loads[n1] += load_val;
                nodal_loads[n2] += load_val;
                nodal_loads[n3] += load_val;
            }
        }
    }

    // Identificar nós de apoio e Distribuir cargas de pilares
    let mut support_nodes = Vec::new();
    for pillar in &model.pillars {
        // Encontrar elemento que contém o pilar para distribuição bilinear
        let i = (pillar.x / dx).floor() as usize;
        let j = (pillar.y / dy).floor() as usize;
        
        if i < model.nx - 1 && j < model.ny - 1 {
            let n0 = j * model.nx + i;
            let n1 = n0 + 1;
            let n2 = n0 + model.nx + 1;
            let n3 = n0 + model.nx;
            
            // Bilinear weights
            let x0 = nodes[n0].0;
            let y0 = nodes[n0].1;
            let xi = (pillar.x - x0) / dx;
            let eta = (pillar.y - y0) / dy;
            
            let w0 = (1.0 - xi) * (1.0 - eta);
            let w1 = xi * (1.0 - eta);
            let w2 = xi * eta;
            let w3 = (1.0 - xi) * eta;
            
            let p_n = pillar.p_kn * 1000.0;
            nodal_loads[n0] += p_n * w0;
            nodal_loads[n1] += p_n * w1;
            nodal_loads[n2] += p_n * w2;
            nodal_loads[n3] += p_n * w3;
            
            // Suporte (Simplificado: nó mais próximo)
            let nodes_quad = [n0, n1, n2, n3];
            let weights = [w0, w1, w2, w3];
            let mut best_idx = 0;
            let mut max_w = -1.0;
            for k in 0..4 {
                if weights[k] > max_w {
                    max_w = weights[k];
                    best_idx = nodes_quad[k];
                }
            }
            support_nodes.push(best_idx);
        }
    }

    SlabMesh { nodes, elements, support_nodes, nodal_loads }
}
