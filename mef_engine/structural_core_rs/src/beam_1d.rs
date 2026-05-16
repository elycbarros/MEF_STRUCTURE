use nalgebra as na;
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Beam1DMember {
    pub id: i32,
    pub node_i: usize,
    pub node_j: usize,
    pub e: f64,
    pub g: f64,
    pub i: f64,
    pub j: f64,
    pub l: f64,
    pub asymmetric_offset: f64,
}

pub fn get_stiffness_matrix(m: &Beam1DMember) -> na::SMatrix<f64, 6, 6> {
    let ei = m.e * m.i;
    let gj = m.g * m.j;
    let l = m.l;
    
    let mut ke = na::SMatrix::<f64, 6, 6>::zeros();
    
    // Flexure (w, theta)
    let f = ei / l.powi(3);
    let kf_data = [
        [12.0, 6.0 * l, -12.0, 6.0 * l],
        [6.0 * l, 4.0 * l.powi(2), -6.0 * l, 2.0 * l.powi(2)],
        [-12.0, -6.0 * l, 12.0, -6.0 * l],
        [6.0 * l, 2.0 * l.powi(2), -6.0 * l, 4.0 * l.powi(2)],
    ];
    
    let flex_indices = [0, 1, 3, 4];
    for (i, &idx_i) in flex_indices.iter().enumerate() {
        for (j, &idx_j) in flex_indices.iter().enumerate() {
            ke[(idx_i, idx_j)] = f * kf_data[i][j];
        }
    }
    
    // Torsion (phi)
    let kt = gj / l;
    ke[(2, 2)] = kt;
    ke[(5, 5)] = kt;
    ke[(2, 5)] = -kt;
    ke[(5, 2)] = -kt;
    
    ke
}

pub fn get_equivalent_nodal_load_uniform(q: f64, l: f64, eccentricity: f64, offset: f64) -> na::SVector<f64, 6> {
    let e_total = eccentricity + offset;
    na::SVector::<f64, 6>::from_column_slice(&[
        -q * l / 2.0,
        q * l.powi(2) / 12.0,
        q * e_total * l / 2.0,
        -q * l / 2.0,
        -q * l.powi(2) / 12.0,
        q * e_total * l / 2.0,
    ])
}

pub fn get_stiffness_matrix_raw(l: f64, e: f64, g: f64, i: f64, j: f64) -> na::SMatrix<f64, 6, 6> {
    let ei = e * i;
    let gj = g * j;
    
    let mut ke = na::SMatrix::<f64, 6, 6>::zeros();
    let f = ei / l.powi(3);
    let kf_data = [
        [12.0, 6.0 * l, -12.0, 6.0 * l],
        [6.0 * l, 4.0 * l.powi(2), -6.0 * l, 2.0 * l.powi(2)],
        [-12.0, -6.0 * l, 12.0, -6.0 * l],
        [6.0 * l, 2.0 * l.powi(2), -6.0 * l, 4.0 * l.powi(2)],
    ];
    let flex_indices = [0, 1, 3, 4];
    for (ri, &idx_i) in flex_indices.iter().enumerate() {
        for (ci, &idx_j) in flex_indices.iter().enumerate() {
            ke[(idx_i, idx_j)] = f * kf_data[ri][ci];
        }
    }
    let kt = gj / l;
    ke[(2, 2)] = kt; ke[(5, 5)] = kt;
    ke[(2, 5)] = -kt; ke[(5, 2)] = -kt;
    ke
}

pub fn get_load_vector_raw(l: f64, q: f64, e_total: f64) -> na::SVector<f64, 6> {
    na::SVector::<f64, 6>::from_column_slice(&[
        q * l / 2.0,            // v1
        -q * l.powi(2) / 12.0,  // m1
        -q * e_total * l / 2.0, // t1
        q * l / 2.0,            // v2
        q * l.powi(2) / 12.0,   // m2
        -q * e_total * l / 2.0, // t2
    ])
}
