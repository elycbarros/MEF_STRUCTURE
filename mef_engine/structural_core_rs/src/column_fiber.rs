use serde::{Serialize, Deserialize};
use pyo3::prelude::*;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Rebar {
    pub x: f64,
    pub y: f64,
    pub area: f64,
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ColumnFiberModel {
    #[pyo3(get, set)]
    pub b: f64,
    #[pyo3(get, set)]
    pub h: f64,
    #[pyo3(get, set)]
    pub fck: f64,
    #[pyo3(get, set)]
    pub fyk: f64,
    #[pyo3(get, set)]
    pub es: f64,
    #[pyo3(get, set)]
    pub rebars: Vec<(f64, f64, f64)>, // (x, y, area)
    #[pyo3(get, set)]
    pub nx: usize,
    #[pyo3(get, set)]
    pub ny: usize,
}

#[pymethods]
impl ColumnFiberModel {
    #[new]
    pub fn new(b: f64, h: f64, fck: f64, fyk: f64, es: f64, rebars: Vec<(f64, f64, f64)>, nx: usize, ny: usize) -> Self {
        Self { b, h, fck, fyk, es, rebars, nx, ny }
    }
}

pub fn get_concrete_stress(eps: f64, fcd: f64) -> f64 {
    // NBR 6118 Parábola-Retângulo
    if eps >= 0.0 {
        return 0.0;
    }
    let abs_eps = eps.abs();
    if abs_eps <= 0.002 {
        0.85 * fcd * (1.0 - (1.0 - abs_eps / 0.002).powi(2))
    } else if abs_eps <= 0.0035 {
        0.85 * fcd
    } else {
        0.0 // Ruptura (simplificado)
    }
}

pub fn get_steel_stress(eps: f64, fyd: f64, es: f64) -> f64 {
    let sig = eps * es;
    if sig.abs() > fyd {
        sig.signum() * fyd
    } else {
        sig
    }
}

pub fn integrate_forces(model: &ColumnFiberModel, eps0: f64, kx: f64, ky: f64) -> (f64, f64, f64) {
    let fcd = model.fck / 1.4 * 1.0e6; // Pa
    let fyd = model.fyk / 1.15 * 1.0e6; // Pa
    
    let dx = model.b / model.nx as f64;
    let dy = model.h / model.ny as f64;
    let fiber_area = dx * dy;
    
    let mut n_c = 0.0;
    let mut mx_c = 0.0;
    let mut my_c = 0.0;
    
    for i in 0..model.nx {
        let x = -model.b / 2.0 + dx / 2.0 + i as f64 * dx;
        for j in 0..model.ny {
            let y = -model.h / 2.0 + dy / 2.0 + j as f64 * dy;
            let eps = eps0 + kx * y + ky * x;
            let sig = get_concrete_stress(eps, fcd);
            n_c += sig * fiber_area;
            mx_c += sig * fiber_area * y;
            my_c += sig * fiber_area * x;
        }
    }
    
    let mut n_s = 0.0;
    let mut mx_s = 0.0;
    let mut my_s = 0.0;
    
    for &(rx, ry, rarea) in &model.rebars {
        let eps = eps0 + kx * ry + ky * rx;
        // Convenção ColumnSolver: compressão positiva. get_steel_stress dá tração positiva.
        let sig = -get_steel_stress(eps, fyd, model.es);
        n_s += sig * rarea;
        mx_s += sig * rarea * ry;
        my_s += sig * rarea * rx;
    }
    
    (n_c + n_s, mx_c + mx_s, my_c + my_s)
}

pub fn solve_equilibrium(model: &ColumnFiberModel, target_n: f64, target_mx: f64, target_my: f64) -> (f64, f64, f64, bool) {
    let mut u = [ -0.001, 0.0, 0.0 ]; // eps0, kx, ky
    let max_iter = 50;
    let tol = 1e-4;
    
    let target = [target_n * 1000.0, target_mx * 1000.0, target_my * 1000.0];
    let scales = [
        target[0].abs().max(100_000.0),
        target[1].abs().max(10_000.0),
        target[2].abs().max(10_000.0)
    ];

    for _ in 0..max_iter {
        let (n, mx, my) = integrate_forces(model, u[0], u[1], u[2]);
        let res = [
            (n - target[0]) / scales[0],
            (mx - target[1]) / scales[1],
            (my - target[2]) / scales[2]
        ];
        
        let norm = (res[0].powi(2) + res[1].powi(2) + res[2].powi(2)).sqrt();
        if norm < tol {
            return (u[0], u[1], u[2], true);
        }
        
        // Jacobiano numérico
        let mut j = [[0.0; 3]; 3];
        let h = 1e-7;
        for i in 0..3 {
            let mut u_h = u;
            u_h[i] += h;
            let (nh, mxh, myh) = integrate_forces(model, u_h[0], u_h[1], u_h[2]);
            let res_h = [
                (nh - target[0]) / scales[0],
                (mxh - target[1]) / scales[1],
                (myh - target[2]) / scales[2]
            ];
            for k in 0..3 {
                j[k][i] = (res_h[k] - res[k]) / h;
            }
        }
        
        // Solve J * du = -res (3x3 inverse)
        let det = j[0][0]*(j[1][1]*j[2][2] - j[1][2]*j[2][1]) -
                  j[0][1]*(j[1][0]*j[2][2] - j[1][2]*j[2][0]) +
                  j[0][2]*(j[1][0]*j[2][1] - j[1][1]*j[2][0]);
                  
        if det.abs() < 1e-18 { break; }
        
        let inv_j = [
            [ (j[1][1]*j[2][2] - j[1][2]*j[2][1])/det, -(j[0][1]*j[2][2] - j[0][2]*j[2][1])/det,  (j[0][1]*j[1][2] - j[0][2]*j[1][1])/det ],
            [-(j[1][0]*j[2][2] - j[1][2]*j[2][0])/det,  (j[0][0]*j[2][2] - j[0][2]*j[2][0])/det, -(j[0][0]*j[1][2] - j[0][2]*j[1][0])/det ],
            [ (j[1][0]*j[2][1] - j[1][1]*j[2][0])/det, -(j[0][0]*j[2][1] - j[0][1]*j[2][0])/det,  (j[0][0]*j[1][1] - j[0][1]*j[1][0])/det ]
        ];
        
        let du = [
            inv_j[0][0]*(-res[0]) + inv_j[0][1]*(-res[1]) + inv_j[0][2]*(-res[2]),
            inv_j[1][0]*(-res[0]) + inv_j[1][1]*(-res[1]) + inv_j[1][2]*(-res[2]),
            inv_j[2][0]*(-res[0]) + inv_j[2][1]*(-res[1]) + inv_j[2][2]*(-res[2])
        ];
        
        // Amortecimento
        u[0] += 0.5 * du[0];
        u[1] += 0.5 * du[1];
        u[2] += 0.5 * du[2];
        
        // Limites físicos
        u[0] = u[0].clamp(-0.0035, 0.010);
        u[1] = u[1].clamp(-0.2, 0.2);
        u[2] = u[2].clamp(-0.2, 0.2);
    }
    
    (u[0], u[1], u[2], false)
}

pub fn generate_interaction_envelope(model: &ColumnFiberModel, axis: char) -> Vec<(f64, f64)> {
    let mut points = Vec::new();
    let h = if axis == 'x' { model.h } else { model.b };
    let n_steps = 50;
    
    // Domínios 1 e 2
    for x_ratio in (0..n_steps/2).map(|i| -1.0 + i as f64 * 1.5 / (n_steps/2) as f64) {
        let eps_max = 0.010;
        let x_pos = x_ratio * h;
        let d = h - 0.04;
        let k = eps_max / (d - x_pos);
        let eps_pivot = -k * x_pos;
        let (n, mx, my) = integrate_forces(model, eps_pivot, if axis == 'x' { k } else { 0.0 }, if axis == 'y' { k } else { 0.0 });
        points.push((n/1000.0, if axis == 'x' { mx/1000.0 } else { my/1000.0 }));
    }
    
    // Domínios 3, 4, 5
    for x_ratio in (0..n_steps/2).map(|i| 0.5 + i as f64 * 2.5 / (n_steps/2) as f64) {
        let eps_min = -0.0035;
        let x_pos = x_ratio * h;
        let k = -eps_min / x_pos;
        let eps_pivot = eps_min + k * (h/2.0);
        let (n, mx, my) = integrate_forces(model, eps_pivot, if axis == 'x' { k } else { 0.0 }, if axis == 'y' { k } else { 0.0 });
        points.push((n/1000.0, if axis == 'x' { mx/1000.0 } else { my/1000.0 }));
    }
    
    points.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
    points
}
