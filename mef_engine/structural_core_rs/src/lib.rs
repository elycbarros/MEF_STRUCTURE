use pyo3::prelude::*;
use faer::Mat;
use faer::prelude::*;
use faer::linalg::solvers::Solve;

#[pyclass]
pub struct BeamSolver {
    pub n_nodes: usize,
    pub stiffness_matrix: Mat<f64>,
    pub load_vector: Mat<f64>,
}

#[pymethods]
impl BeamSolver {
    #[new]
    fn new(n_spans: usize) -> Self {
        let n_nodes = n_spans + 1;
        let n_dof = n_nodes * 2;
        Self {
            n_nodes,
            stiffness_matrix: Mat::zeros(n_dof, n_dof),
            load_vector: Mat::zeros(n_dof, 1),
        }
    }

    fn add_span_stiffness(&mut self, node_i: usize, node_j: usize, l: f64, e: f64, i: f64) {
        let ei = e * i;
        let l_val = l;
        let l2 = l_val * l_val;
        let l3 = l2 * l_val;

        let k_local = [
            [12.0 * ei / l3, 6.0 * ei / l2, -12.0 * ei / l3, 6.0 * ei / l2],
            [6.0 * ei / l2, 4.0 * ei / l_val, -6.0 * ei / l2, 2.0 * ei / l_val],
            [-12.0 * ei / l3, -6.0 * ei / l2, 12.0 * ei / l3, -6.0 * ei / l2],
            [6.0 * ei / l2, 2.0 * ei / l_val, -6.0 * ei / l2, 4.0 * ei / l_val],
        ];

        let dofs = [node_i * 2, node_i * 2 + 1, node_j * 2, node_j * 2 + 1];

        for (r_idx, &global_row) in dofs.iter().enumerate() {
            for (c_idx, &global_col) in dofs.iter().enumerate() {
                self.stiffness_matrix[(global_row, global_col)] += k_local[r_idx][c_idx];
            }
        }
    }

    fn add_point_load(&mut self, node_idx: usize, value_kn: f64) {
        let dof = node_idx * 2;
        self.load_vector[(dof, 0)] -= value_kn; // Downward is positive in load but negative in DOF
    }

    fn solve(&self, fixed_dofs: Vec<usize>) -> PyResult<Vec<f64>> {
        let n = self.stiffness_matrix.nrows();
        let mut k_comp = self.stiffness_matrix.clone();
        let f_comp = self.load_vector.clone();

        // Penalty Method for Boundary Conditions
        let penalty = 1e20;
        for &dof in &fixed_dofs {
            if dof < n {
                k_comp[(dof, dof)] += penalty;
            }
        }

        // Solve K * d = F
        let lu = k_comp.full_piv_lu();
        let solution = lu.solve(&f_comp);
        
        let mut results = Vec::with_capacity(n);
        for i in 0..n {
            results.push(solution[(i, 0)]);
        }
        Ok(results)
    }

    fn get_matrix_size(&self) -> (usize, usize) {
        (self.stiffness_matrix.nrows(), self.stiffness_matrix.ncols())
    }
}

/// Seção Transversal de Viga
#[pyclass]
pub struct BeamCrossSection {
    pub b: f64, // largura
    pub h: f64, // altura
}

#[pymethods]
impl BeamCrossSection {
    #[new]
    fn new(b: f64, h: f64) -> Self {
        Self { b, h }
    }

    fn area(&self) -> f64 { self.b * self.h }
    fn inertia(&self) -> f64 { (self.b * self.h.powi(3)) / 12.0 }
    fn cg_y(&self) -> f64 { self.h / 2.0 }
}

/// Módulo TensionPro: Concreto Protendido (NBR 6118)
#[pyclass]
pub struct TensionPro {
    pub fck: f64,
}

#[pymethods]
impl TensionPro {
    #[new]
    fn new(fck: f64) -> Self {
        Self { fck }
    }

    /// Cálculo de perda por atrito (Pós-tração)
    /// P(x) = P0 * e^(-mu * (theta + k*x))
    fn calculate_friction_loss(&self, p0: f64, mu: f64, k: f64, x: f64, theta_rad: f64) -> f64 {
        p0 * (-mu * (theta_rad + k * x)).exp()
    }

    /// Estimativa de Perda Progressiva Total (Simplificada para pré-dimensionamento)
    /// Retorna a força residual considerando perdas de 15% a 25%
    fn estimate_total_progressive_losses(&self, p_initial: f64, is_post_tension: bool) -> f64 {
        let factor = if is_post_tension { 0.80 } else { 0.75 };
        p_initial * factor
    }

    /// Módulo de Elasticidade do Concreto (Ecs) - NBR 6118
    /// fck em MPa, retorna em GPa
    fn e_cs(&self) -> f64 {
        let alpha_e = 1.0; // Basalto/Diabásio. Para granito 0.9, calcário 0.8
        let e_ci = alpha_e * 5600.0 * self.fck.sqrt();
        (0.8 + 0.2 * self.fck / 80.0) * e_ci / 1000.0
    }

    /// Deformação de Retração (NBR 6118)
    /// t_days: tempo em dias
    /// h_0: espessura fictícia (2 * Area / Perímetro) em cm
    fn shrinkage_strain(&self, t_days: f64, h_0: f64) -> f64 {
        let epsilon_cs_inf = -0.0005; // Valor base para RH 70%
        let beta_s = (t_days / (t_days + 0.035 * h_0.powi(2))).sqrt();
        epsilon_cs_inf * beta_s
    }

    /// Coeficiente de Fluência (phi) - NBR 6118
    /// t0_days: idade ao carregar
    /// t_days: idade atual
    fn creep_coefficient(&self, t0_days: f64, t_days: f64) -> f64 {
        let phi_0 = 2.5; // Valor base
        let beta_c = ((t_days - t0_days) / (t_days - t0_days + 20.0)).sqrt();
        phi_0 * beta_c
    }

    /// Cálculo de Perda por Relaxação do Aço (Relaxação Normal - Classe I)
    /// fpk: resistência característica do aço (ex: 1900 MPa)
    /// sigma_pi: tensão inicial
    fn steel_relaxation_loss(&self, sigma_pi: f64, fpk: f64, t_hours: f64) -> f64 {
        let ratio = sigma_pi / fpk;
        if ratio < 0.5 { return 0.0; }
        let psi = 10.0 * (ratio - 0.5).powi(2);
        sigma_pi * psi * (t_hours / 1000.0).powf(0.15)
    }
}

#[pymodule]
fn structural_core_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<BeamSolver>()?;
    m.add_class::<TensionPro>()?;
    m.add_class::<BeamCrossSection>()?;
    Ok(())
}
