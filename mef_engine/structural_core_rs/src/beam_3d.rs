use serde::{Serialize, Deserialize};
use nalgebra as na;
use na::DMatrix;
use pyo3::prelude::*;

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
}

#[derive(Debug, Clone, Serialize, Deserialize, FromPyObject)]
pub struct Material {
    pub e: f64,
    pub g: f64,
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

/// Matriz de rigidez elástica local (12x12) para viga 3D
pub fn local_stiffness_matrix(l: f64, e: f64, g: f64, a: f64, iy: f64, iz: f64, j: f64) -> DMatrix<f64> {
    let mut k = DMatrix::zeros(12, 12);
    let l2 = l * l;
    let l3 = l2 * l;

    // Axial
    let ea_l = e * a / l;
    k[(0, 0)] = ea_l; k[(6, 6)] = ea_l;
    k[(0, 6)] = -ea_l; k[(6, 0)] = -ea_l;

    // Torsional
    let gj_l = g * j / l;
    k[(3, 3)] = gj_l; k[(9, 9)] = gj_l;
    k[(3, 9)] = -gj_l; k[(9, 3)] = -gj_l;

    // Bending XY (z-local)
    let fz = e * iz / l3;
    k[(1, 1)] = 12.0 * fz; k[(7, 7)] = 12.0 * fz;
    k[(1, 7)] = -12.0 * fz; k[(7, 1)] = -12.0 * fz;
    k[(1, 5)] = 6.0 * l * fz; k[(5, 1)] = 6.0 * l * fz;
    k[(1, 11)] = 6.0 * l * fz; k[(11, 1)] = 6.0 * l * fz;
    k[(7, 5)] = -6.0 * l * fz; k[(5, 7)] = -6.0 * l * fz;
    k[(7, 11)] = -6.0 * l * fz; k[(11, 7)] = -6.0 * l * fz;
    k[(5, 5)] = 4.0 * l2 * fz; k[(11, 11)] = 4.0 * l2 * fz;
    k[(5, 11)] = 2.0 * l2 * fz; k[(11, 5)] = 2.0 * l2 * fz;

    // Bending XZ (y-local)
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

/// Matriz de rigidez geométrica local (12x12) para efeito P-Delta
/// Baseado em McGuire, Gallagher, Ziemian (Matrix Structural Analysis)
pub fn local_geometric_stiffness_matrix(l: f64, p: f64) -> DMatrix<f64> {
    let mut kg = DMatrix::zeros(12, 12);
    if l < 1e-6 { return kg; }
    let p_l = p / l;
    let p_l_30 = p * l / 30.0;
    
    // Translação Y e Z
    kg[(1, 1)] = 1.2 * p_l;  kg[(7, 7)] = 1.2 * p_l;
    kg[(1, 7)] = -1.2 * p_l; kg[(7, 1)] = -1.2 * p_l;
    
    kg[(2, 2)] = 1.2 * p_l;  kg[(8, 8)] = 1.2 * p_l;
    kg[(2, 8)] = -1.2 * p_l; kg[(8, 2)] = -1.2 * p_l;

    // Momentos
    kg[(1, 5)] = 0.1 * p;    kg[(5, 1)] = 0.1 * p;
    kg[(1, 11)] = 0.1 * p;   kg[(11, 1)] = 0.1 * p;
    kg[(7, 5)] = -0.1 * p;   kg[(5, 7)] = -0.1 * p;
    kg[(7, 11)] = -0.1 * p;  kg[(11, 7)] = -0.1 * p;
    
    kg[(2, 4)] = -0.1 * p;   kg[(4, 2)] = -0.1 * p;
    kg[(2, 10)] = -0.1 * p;  kg[(10, 2)] = -0.1 * p;
    kg[(8, 4)] = 0.1 * p;    kg[(4, 8)] = 0.1 * p;
    kg[(8, 10)] = 0.1 * p;   kg[(10, 8)] = 0.1 * p;

    // Rotações
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

    if cx.abs() < 1e-6 && cy.abs() < 1e-6 { // Vertical
        uy = if cz > 0.0 {
            na::Vector3::new(0.0, 1.0, 0.0)
        } else {
            na::Vector3::new(0.0, -1.0, 0.0)
        };
    } else {
        uy = na::Vector3::new(0.0, 0.0, 1.0);
    }

    let uz = ux.cross(&uy).normalize();
    let uy_corrected = uz.cross(&ux).normalize();

    let r_sub = na::Matrix3::from_rows(&[
        ux.transpose(),
        uy_corrected.transpose(),
        uz.transpose(),
    ]);

    let mut t = DMatrix::zeros(12, 12);
    for i in 0..4 {
        t.fixed_view_mut::<3, 3>(i * 3, i * 3).copy_from(&r_sub);
    }

    (t, l)
}
