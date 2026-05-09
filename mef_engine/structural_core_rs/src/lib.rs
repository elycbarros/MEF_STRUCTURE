use pyo3::prelude::*;
use serde::{Serialize, Deserialize};
use rayon::prelude::*;
pub use faer::prelude::*;
use faer::sparse::linalg::lu::SymbolicLu;
use faer::sparse::linalg::solvers::Lu;
use numpy::{PyArray1, IntoPyArray};
use std::collections::HashMap;

// ----------------------------
// Modelos de dados
// ----------------------------
#[derive(Debug, Clone, Serialize, Deserialize, FromPyObject)]
pub struct Node3D {
    pub id: i32,
    pub x: f64,
    pub y: f64,
    pub z: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromPyObject)]
pub struct SectionProperties {
    pub area: f64,
    pub iy: f64,
    pub iz: f64,
    pub j: f64,
    pub ey: f64,
    pub ez: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromPyObject)]
pub struct Material {
    pub e: f64,
    pub g: f64,
    pub nu: f64,
    pub rho: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize, FromPyObject)]
pub struct Beam3D {
    pub id: i32,
    pub node_i: i32,
    pub node_j: i32,
    pub section: SectionProperties,
    pub material: Material,
    pub member_type: String, 
}

mod beam_3d_utils {
    use nalgebra as na;
    use na::{DMatrix};
    use super::{Node3D};

    pub fn local_stiffness_matrix(l: f64, e: f64, g: f64, a: f64, iy: f64, iz: f64, j: f64) -> DMatrix<f64> {
        let mut k = DMatrix::zeros(12, 12);
        let l2 = l * l;
        let l3 = l2 * l;
        let ea_l = e * a / l;
        k[(0, 0)] = ea_l; k[(6, 6)] = ea_l;
        k[(0, 6)] = -ea_l; k[(6, 0)] = -ea_l;
        let gj_l = g * j / l;
        k[(3, 3)] = gj_l; k[(9, 9)] = gj_l;
        k[(3, 9)] = -gj_l; k[(9, 3)] = -gj_l;
        let fz = e * iz / l3;
        k[(1, 1)] = 12.0 * fz; k[(7, 7)] = 12.0 * fz;
        k[(1, 7)] = -12.0 * fz; k[(7, 1)] = -12.0 * fz;
        k[(1, 5)] = 6.0 * l * fz; k[(5, 1)] = 6.0 * l * fz;
        k[(1, 11)] = 6.0 * l * fz; k[(11, 1)] = 6.0 * l * fz;
        k[(7, 5)] = -6.0 * l * fz; k[(5, 7)] = -6.0 * l * fz;
        k[(7, 11)] = -6.0 * l * fz; k[(11, 7)] = -6.0 * l * fz;
        k[(5, 5)] = 4.0 * l2 * fz; k[(11, 11)] = 4.0 * l2 * fz;
        k[(5, 11)] = 2.0 * l2 * fz; k[(11, 5)] = 2.0 * l2 * fz;
        let fy = e * iy / l3;
        k[(2, 2)] = 12.0 * fy; k[(8, 8)] = 12.0 * fy;
        k[(2, 8)] = -12.0 * fy; k[(8, 2)] = -12.0 * fy;
        k[(2, 4)] = -6.0 * l * fy; k[(4, 2)] = -6.0 * l * fy;
        k[(2, 10)] = -6.0 * l * fy; k[(10, 2)] = -6.0 * l * fy;
        k[(8, 4)] = 6.0 * l * fy; k[(4, 8)] = 6.0 * l * fy;
        k[(8, 10)] = 6.0 * l * fy; k[(10, 8)] = 6.0 * l * fy;
        k[(4, 4)] = 4.0 * l2 * fy; k[(10, 10)] = 4.0 * l2 * fy;
        k[(4, 10)] = 2.0 * l2 * fy; k[(10, 4)] = 2.0 * l2 * fy;
        k
    }

    pub fn local_geometric_stiffness_matrix(l: f64, p: f64) -> DMatrix<f64> {
        let mut kg = DMatrix::zeros(12, 12);
        if l < 1e-6 { return kg; }
        let p_l = p / l;
        let p_l_30 = p * l / 30.0;
        kg[(1, 1)] = 1.2 * p_l;  kg[(7, 7)] = 1.2 * p_l;
        kg[(1, 7)] = -1.2 * p_l; kg[(7, 1)] = -1.2 * p_l;
        kg[(2, 2)] = 1.2 * p_l;  kg[(8, 8)] = 1.2 * p_l;
        kg[(2, 8)] = -1.2 * p_l; kg[(8, 2)] = -1.2 * p_l;
        kg[(1, 5)] = 0.1 * p;    kg[(5, 1)] = 0.1 * p;
        kg[(1, 11)] = 0.1 * p;   kg[(11, 1)] = 0.1 * p;
        kg[(7, 5)] = -0.1 * p;   kg[(5, 7)] = -0.1 * p;
        kg[(7, 11)] = -0.1 * p;  kg[(11, 7)] = -0.1 * p;
        kg[(2, 4)] = -0.1 * p;   kg[(4, 2)] = -0.1 * p;
        kg[(2, 10)] = -0.1 * p;  kg[(10, 2)] = -0.1 * p;
        kg[(8, 4)] = 0.1 * p;    kg[(4, 8)] = 0.1 * p;
        kg[(8, 10)] = 0.1 * p;   kg[(10, 8)] = 0.1 * p;
        kg[(5, 5)] = 4.0 * p_l_30;   kg[(11, 11)] = 4.0 * p_l_30;
        kg[(5, 11)] = -p_l_30;       kg[(11, 5)] = -p_l_30;
        kg[(4, 4)] = 4.0 * p_l_30;   kg[(10, 10)] = 4.0 * p_l_30;
        kg[(4, 10)] = -p_l_30;       kg[(10, 4)] = -p_l_30;
        kg
    }

    pub fn rotation_matrix(n1: &Node3D, n2: &Node3D) -> (DMatrix<f64>, f64) {
        let dx = n2.x - n1.x;
        let dy = n2.y - n1.y;
        let dz = n2.z - n1.z;
        let l = (dx*dx + dy*dy + dz*dz).sqrt();
        let cx = dx / l;
        let cy = dy / l;
        let cz = dz / l;
        let ux = na::Vector3::new(cx, cy, cz);
        let uy: na::Vector3<f64>;
        if cx.abs() < 1e-6 && cy.abs() < 1e-6 {
            uy = if cz > 0.0 { na::Vector3::new(0.0, 1.0, 0.0) } else { na::Vector3::new(0.0, -1.0, 0.0) };
        } else {
            uy = na::Vector3::new(0.0, 0.0, 1.0);
        }
        let uz = ux.cross(&uy).normalize();
        let uy_corrected = uz.cross(&ux).normalize();
        let r_sub = na::Matrix3::from_rows(&[ux.transpose(), uy_corrected.transpose(), uz.transpose()]);
        let mut t = DMatrix::zeros(12, 12);
        for i in 0..4 { t.fixed_view_mut::<3, 3>(i * 3, i * 3).copy_from(&r_sub); }
        (t, l)
    }
}

#[pyfunction]
#[pyo3(signature = (nodes, beams, loads_vec, fixed_dofs, reduce_stiffness, axial_loads=None))]
fn solve_frame_3d(
    py: Python,
    nodes: Vec<Node3D>,
    beams: Vec<Beam3D>,
    loads_vec: Vec<f64>,
    fixed_dofs: Vec<usize>,
    reduce_stiffness: bool,
    axial_loads: Option<HashMap<i32, f64>>,
) -> PyResult<Py<PyArray1<f64>>> {
    let n_nodes = nodes.len();
    let n_dofs = n_nodes * 6;
    let mut rhs = loads_vec;

    let mut node_index = HashMap::new();
    let mut sorted_nodes = nodes.clone();
    sorted_nodes.sort_by_key(|n| n.id);
    for (i, n) in sorted_nodes.iter().enumerate() {
        node_index.insert(n.id, i);
    }
    
    let node_map = &node_index;
    let nodes_dict: HashMap<i32, &Node3D> = nodes.iter().map(|n| (n.id, n)).collect();
    let nodes_dict_ref = &nodes_dict;

    let entries: Vec<(usize, usize, f64)> = beams
        .par_iter()
        .flat_map(|beam| {
            let n1 = nodes_dict_ref.get(&beam.node_i).expect("Node I not found");
            let n2 = nodes_dict_ref.get(&beam.node_j).expect("Node J not found");
            let (t, l) = beam_3d_utils::rotation_matrix(n1, n2);
            let mut k_local = beam_3d_utils::local_stiffness_matrix(
                l, beam.material.e, beam.material.g, beam.section.area,
                beam.section.iy, beam.section.iz, beam.section.j
            );
            if reduce_stiffness {
                let factor = if beam.member_type == "column" { 0.8 } else { 0.4 };
                k_local *= factor;
            }
            if let Some(ref loads_map) = axial_loads {
                if let Some(&p) = loads_map.get(&beam.id) {
                    k_local += beam_3d_utils::local_geometric_stiffness_matrix(l, p);
                }
            }
            let k_global = t.transpose() * k_local * t;
            let i_idx = *node_map.get(&beam.node_i).unwrap();
            let j_idx = *node_map.get(&beam.node_j).unwrap();
            let dofs = [
                i_idx * 6, i_idx * 6 + 1, i_idx * 6 + 2, i_idx * 6 + 3, i_idx * 6 + 4, i_idx * 6 + 5,
                j_idx * 6, j_idx * 6 + 1, j_idx * 6 + 2, j_idx * 6 + 3, j_idx * 6 + 4, j_idx * 6 + 5,
            ];
            let mut local_triplets = Vec::with_capacity(144);
            for r in 0..12 {
                for c in 0..12 {
                    let val = k_global[(r, c)];
                    if val.abs() > 1e-15 { local_triplets.push((dofs[r], dofs[c], val)); }
                }
            }
            local_triplets
        })
        .collect();

    let mut final_entries = entries;
    let penalty = 1e20;
    for &dof in &fixed_dofs {
        if dof < n_dofs {
            final_entries.push((dof, dof, penalty));
            rhs[dof] = 0.0;
        }
    }

    let k_csc = faer::sparse::SparseColMat::<usize, f64>::try_new_from_triplets(n_dofs, n_dofs, &final_entries)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("CSC build failed: {:?}", e)))?;
    
    let f = Mat::<f64>::from_fn(n_dofs, 1, |i, _| rhs[i]);
    
    let lu = k_csc.sp_lu().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("LU failed: {:?}", e)))?;
    let u = lu.solve(&f);
    
    let mut u_vec = vec![0.0; n_dofs];
    for i in 0..n_dofs { u_vec[i] = u[(i, 0)]; }

    Ok(u_vec.into_pyarray(py).to_owned())
}

#[pymodule]
fn structural_core_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(solve_frame_3d, m)?)?;
    Ok(())
}
