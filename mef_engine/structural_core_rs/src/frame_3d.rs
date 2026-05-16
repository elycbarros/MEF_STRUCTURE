use nalgebra as na;
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Frame3DMember {
    pub id: i32,
    pub node_i: usize,
    pub node_j: usize,
    pub e: f64,
    pub g: f64,
    pub area: f64,
    pub iy: f64,
    pub iz: f64,
    pub j: f64,
    pub l: f64,
}

pub fn get_transformation_matrix(n1: (f64, f64, f64), n2: (f64, f64, f64)) -> na::SMatrix<f64, 12, 12> {
    let dx = n2.0 - n1.0;
    let dy = n2.1 - n1.1;
    let dz = n2.2 - n1.2;
    let l = (dx * dx + dy * dy + dz * dz).sqrt();
    
    let cx = dx / l;
    let cy = dy / l;
    let cz = dz / l;
    
    // Local x-axis
    let ux = na::Vector3::new(cx, cy, cz);
    
    // Orientation of local y-axis
    let mut uy = if cx.abs() < 1e-6 && cy.abs() < 1e-6 {
        if cz > 0.0 { na::Vector3::new(0.0, 1.0, 0.0) } else { na::Vector3::new(0.0, -1.0, 0.0) }
    } else {
        na::Vector3::new(0.0, 0.0, 1.0)
    };
    
    let uz = ux.cross(&uy).normalize();
    uy = uz.cross(&ux).normalize();
    
    let mut t_sub = na::Matrix3::zeros();
    t_sub.row_mut(0).copy_from(&ux.transpose());
    t_sub.row_mut(1).copy_from(&uy.transpose());
    t_sub.row_mut(2).copy_from(&uz.transpose());
    
    let mut t = na::SMatrix::<f64, 12, 12>::zeros();
    for i in 0..4 {
        t.fixed_view_mut::<3, 3>(3 * i, 3 * i).copy_from(&t_sub);
    }
    t
}

pub fn get_stiffness_matrix(m: &Frame3DMember, p: f64) -> na::SMatrix<f64, 12, 12> {
    let e = m.e;
    let g = m.g;
    let a = m.area;
    let iy = m.iy;
    let iz = m.iz;
    let j = m.j;
    let l = m.l;
    
    let mut ke = na::SMatrix::<f64, 12, 12>::zeros();
    
    // Axial
    let k_axial = e * a / l;
    ke[(0, 0)] = k_axial; ke[(6, 6)] = k_axial;
    ke[(0, 6)] = -k_axial; ke[(6, 0)] = -k_axial;
    
    // Torsional
    let k_torsion = g * j / l;
    ke[(3, 3)] = k_torsion; ke[(9, 9)] = k_torsion;
    ke[(3, 9)] = -k_torsion; ke[(9, 3)] = -k_torsion;
    
    // Bending XY (z-local)
    let fz = e * iz / l.powi(3);
    ke[(1, 1)] = 12.0 * fz; ke[(7, 7)] = 12.0 * fz;
    ke[(1, 7)] = -12.0 * fz; ke[(7, 1)] = -12.0 * fz;
    ke[(1, 5)] = 6.0 * l * fz; ke[(5, 1)] = 6.0 * l * fz;
    ke[(1, 11)] = 6.0 * l * fz; ke[(11, 1)] = 6.0 * l * fz;
    ke[(7, 5)] = -6.0 * l * fz; ke[(5, 7)] = -6.0 * l * fz;
    ke[(7, 11)] = -6.0 * l * fz; ke[(11, 7)] = -6.0 * l * fz;
    ke[(5, 5)] = 4.0 * l.powi(2) * fz; ke[(11, 11)] = 4.0 * l.powi(2) * fz;
    ke[(5, 11)] = 2.0 * l.powi(2) * fz; ke[(11, 5)] = 2.0 * l.powi(2) * fz;
    
    // Bending XZ (y-local)
    let fy = e * iy / l.powi(3);
    ke[(2, 2)] = 12.0 * fy; ke[(8, 8)] = 12.0 * fy;
    ke[(2, 8)] = -12.0 * fy; ke[(8, 2)] = -12.0 * fy;
    ke[(2, 4)] = -6.0 * l * fy; ke[(4, 2)] = -6.0 * l * fy;
    ke[(2, 10)] = -6.0 * l * fy; ke[(10, 2)] = -6.0 * l * fy;
    ke[(8, 4)] = 6.0 * l * fy; ke[(4, 8)] = 6.0 * l * fy;
    ke[(8, 10)] = 6.0 * l * fy; ke[(10, 8)] = 6.0 * l * fy;
    ke[(4, 4)] = 4.0 * l.powi(2) * fy; ke[(10, 10)] = 4.0 * l.powi(2) * fy;
    ke[(4, 10)] = 2.0 * l.powi(2) * fy; ke[(10, 4)] = 2.0 * l.powi(2) * fy;
    
    if p.abs() > 1e-3 {
        let phi = p / l;
        let mut kg = na::SMatrix::<f64, 12, 12>::zeros();
        
        // Translations
        for i in [1, 2, 7, 8] { kg[(i, i)] = 1.2 * phi; }
        for (i, j) in [(1, 7), (7, 1), (2, 8), (8, 2)] { kg[(i, j)] = -1.2 * phi; }
        
        // Trans-Rot coupling
        for (i, j) in [(1, 5), (5, 1), (1, 11), (11, 1), (8, 4), (4, 8), (8, 10), (10, 8)] { kg[(i, j)] = 0.1 * l * phi; }
        for (i, j) in [(7, 5), (5, 7), (7, 11), (11, 7), (2, 4), (4, 2), (2, 10), (10, 2)] { kg[(i, j)] = -0.1 * l * phi; }
        
        // Rotations
        for i in [4, 5, 10, 11] { kg[(i, i)] = 0.133 * l.powi(2) * phi; }
        for (i, j) in [(4, 10), (10, 4), (5, 11), (11, 5)] { kg[(i, j)] = -0.033 * l.powi(2) * phi; }
        
        return ke + kg;
    }
    
    ke
}
