use nalgebra as na;
use na::{DMatrix, DVector};

pub fn local_stiffness_matrix(
    coords: &na::Matrix4x2<f64>,
    e: f64,
    nu: f64,
    h: f64,
) -> DMatrix<f64> {
    let mut ke = DMatrix::zeros(12, 12);
    
    // Propriedades de flexão
    let d = e * h.powi(3) / (12.0 * (1.0 - nu * nu));
    let db = na::Matrix3::new(
        d, d * nu, 0.0,
        d * nu, d, 0.0,
        0.0, 0.0, d * (1.0 - nu) / 2.0,
    );
    
    // Propriedades de cisalhamento
    let g = e / (2.0 * (1.0 + nu));
    let ks = 5.0 / 6.0;
    let ds = ks * g * h;
    
    // Integração de Gauss para flexão (2x2)
    let gp = 1.0 / 3.0f64.sqrt();
    let gauss_flex = [(-gp, -gp), (gp, -gp), (gp, gp), (-gp, gp)];
    let weight_flex = 1.0;
    
    for (xi, eta) in gauss_flex {
        let (n, dndxi) = shape_functions(xi, eta);
        let j = dndxi.transpose() * coords;
        let det_j = j.determinant();
        let inv_j = j.try_inverse().expect("Jacobian not invertible");
        let dndxy = dndxi * inv_j;
        let mut bb = na::DMatrix::zeros(3, 12);
        for i in 0..4 {
            bb[(0, 3 * i + 1)] = dndxy[(i, 0)];
            bb[(1, 3 * i + 2)] = dndxy[(i, 1)];
            bb[(2, 3 * i + 1)] = dndxy[(i, 1)];
            bb[(2, 3 * i + 2)] = dndxy[(i, 0)];
        }
        
        ke += (bb.transpose() * db * bb) * det_j * weight_flex;
    }
    
    // Integração seletiva para cisalhamento (1x1) - Evita Shear Locking
    let xi_s = 0.0;
    let eta_s = 0.0;
    let weight_shear = 4.0; // 2 * 2 weight for 1 point integration in [-1, 1]
    
    let (n, dndxi) = shape_functions(xi_s, eta_s);
    let j = dndxi.transpose() * coords;
    let det_j = j.determinant();
    let inv_j = j.try_inverse().expect("Jacobian not invertible");
    let dndxy = dndxi * inv_j;
    
    let mut bs = na::DMatrix::zeros(2, 12);
    for i in 0..4 {
        bs[(0, 3 * i)] = dndxy[(i, 0)];
        bs[(0, 3 * i + 1)] = -n[i];
        bs[(1, 3 * i)] = dndxy[(i, 1)];
        bs[(1, 3 * i + 2)] = -n[i];
    }
    
    ke += (bs.transpose() * bs) * ds * det_j * weight_shear;
    
    ke
}

fn shape_functions(xi: f64, eta: f64) -> (na::Vector4<f64>, na::Matrix4x2<f64>) {
    let n = na::Vector4::new(
        0.25 * (1.0 - xi) * (1.0 - eta),
        0.25 * (1.0 + xi) * (1.0 - eta),
        0.25 * (1.0 + xi) * (1.0 + eta),
        0.25 * (1.0 - xi) * (1.0 + eta),
    );
    
    let mut dndxi = na::Matrix4x2::zeros();
    dndxi[(0, 0)] = -0.25 * (1.0 - eta);
    dndxi[(0, 1)] = -0.25 * (1.0 - xi);
    
    dndxi[(1, 0)] =  0.25 * (1.0 - eta);
    dndxi[(1, 1)] = -0.25 * (1.0 + xi);
    
    dndxi[(2, 0)] =  0.25 * (1.0 + eta);
    dndxi[(2, 1)] =  0.25 * (1.0 + xi);
    
    dndxi[(3, 0)] = -0.25 * (1.0 + eta);
    dndxi[(3, 1)] =  0.25 * (1.0 - xi);
    
    (n, dndxi)
}

pub fn compute_efforts(
    coords: &na::Matrix4x2<f64>,
    u_el: &na::DVector<f64>,
    e: f64,
    nu: f64,
    h: f64,
) -> (f64, f64, f64, f64, f64) {
    let d = e * h.powi(3) / (12.0 * (1.0 - nu * nu));
    let db = na::Matrix3::new(
        d, d * nu, 0.0,
        d * nu, d, 0.0,
        0.0, 0.0, d * (1.0 - nu) / 2.0,
    );
    
    let g = e / (2.0 * (1.0 + nu));
    let ks = 5.0 / 6.0;
    let ds = ks * g * h;

    // Calcular no centro (0, 0)
    let (n, dndxi) = shape_functions(0.0, 0.0);
    let j = dndxi.transpose() * coords;
    let inv_j = j.try_inverse().expect("Jacobian not invertible");
    let dndxy = dndxi * inv_j;

    let mut bb = na::DMatrix::zeros(3, 12);
    let mut bs = na::DMatrix::zeros(2, 12);
    
    for i in 0..4 {
        bb[(0, 3 * i + 1)] = dndxy[(i, 0)];
        bb[(1, 3 * i + 2)] = dndxy[(i, 1)];
        bb[(2, 3 * i + 1)] = dndxy[(i, 1)];
        bb[(2, 3 * i + 2)] = dndxy[(i, 0)];

        bs[(0, 3 * i)] = dndxy[(i, 0)];
        bs[(0, 3 * i + 1)] = -n[i];
        bs[(1, 3 * i)] = dndxy[(i, 1)];
        bs[(1, 3 * i + 2)] = -n[i];
    }

    let kappa = bb * u_el;
    let m = db * kappa;
    
    let gamma = bs * u_el;
    let v = gamma * ds;

    (m[0], m[1], m[2], v[0], v[1])
}
