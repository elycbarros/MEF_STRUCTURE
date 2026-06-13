use nalgebra as na;
use faer::prelude::*;
use faer::sparse::linalg::solvers::Lu;

/// Encontra o painel (4 nós) que contém o ponto (x, y) e retorna pesos bilineares.
fn find_cell_weights(
    xs: &[f64],
    ys: &[f64],
    nx: usize,
    x: f64,
    y: f64,
) -> ([usize; 4], [f64; 4]) {
    let x_clamped = x.clamp(xs[0], xs[xs.len() - 1]);
    let y_clamped = y.clamp(ys[0], ys[ys.len() - 1]);

    let ix = match xs.binary_search_by(|v| v.partial_cmp(&x_clamped).unwrap()) {
        Ok(i) => i.min(xs.len() - 2),
        Err(i) => i.max(1).min(xs.len() - 1) - 1,
    };
    let iy = match ys.binary_search_by(|v| v.partial_cmp(&y_clamped).unwrap()) {
        Ok(i) => i.min(ys.len() - 2),
        Err(i) => i.max(1).min(ys.len() - 1) - 1,
    };

    let x1 = xs[ix];
    let x2 = xs[ix + 1];
    let y1 = ys[iy];
    let y2 = ys[iy + 1];

    let tx = if (x2 - x1).abs() < 1e-15 { 0.0 } else { (x_clamped - x1) / (x2 - x1) };
    let ty = if (y2 - y1).abs() < 1e-15 { 0.0 } else { (y_clamped - y1) / (y2 - y1) };

    let n0 = iy * nx + ix;
    let n1 = n0 + 1;
    let n2 = n0 + nx + 1;
    let n3 = n0 + nx;

    let w0 = (1.0 - tx) * (1.0 - ty);
    let w1 = tx * (1.0 - ty);
    let w2 = tx * ty;
    let w3 = (1.0 - tx) * ty;
    let sum = w0 + w1 + w2 + w3;
    let s = if sum > 1e-15 { 1.0 / sum } else { 1.0 };

    ([n0, n1, n2, n3], [w0 * s, w1 * s, w2 * s, w3 * s])
}

/// Monta K esparso (triplets) e vetor RHS para radier sobre Winkler.
/// Retorna (row, col, val, rhs, distributed_load_total, column_load_total, nodal_column_loads_flat).
#[allow(clippy::too_many_arguments)]
pub fn assemble_system(
    nodes_xy: &[f64],
    elements: &[usize],
    tributary_areas: &[f64],
    xs: &[f64],
    ys: &[f64],
    nx: usize,
    stiffness_factors: &[f64],
    h_per_element: &[f64],
    opening_mask: &[bool],
    kv_nodal: &[f64],
    active_springs: &[bool],
    e: f64,
    nu: f64,
    h_default: f64,
    q_uniform: f64,
    column_loads: &[f64],
    area_load_xmin: &[f64],
    area_load_ymin: &[f64],
    area_load_xmax: &[f64],
    area_load_ymax: &[f64],
    area_load_q: &[f64],
    supp_x: &[f64],
    supp_y: &[f64],
    supp_kz: &[f64],
    supp_krx: &[f64],
    supp_kry: &[f64],
    pile_x: &[f64],
    pile_y: &[f64],
    pile_k: &[f64],
    penalty: f64,
) -> (Vec<usize>, Vec<usize>, Vec<f64>, Vec<f64>, f64, f64, Vec<f64>) {
    let n_nodes = nodes_xy.len() / 2;
    let n_elements = elements.len() / 4;
    let ndof = n_nodes * 3;

    let mut row_idx = Vec::new();
    let mut col_idx = Vec::new();
    let mut data_val = Vec::new();
    let mut rhs = vec![0.0; ndof];
    let mut nodal_column_loads = vec![0.0; n_nodes];
    let mut distributed_load_total = 0.0;
    let mut column_load_total = 0.0;

    let node_coords: Vec<(f64, f64)> = (0..n_nodes)
        .map(|i| (nodes_xy[2 * i], nodes_xy[2 * i + 1]))
        .collect();

    // --- Element stiffness ---
    for ie in 0..n_elements {
        if !opening_mask.is_empty() && ie < opening_mask.len() && opening_mask[ie] {
            continue;
        }
        let el = &elements[ie * 4..ie * 4 + 4];
        let mut coords = na::Matrix4x2::zeros();
        for (i, &nid) in el.iter().enumerate() {
            coords[(i, 0)] = node_coords[nid].0;
            coords[(i, 1)] = node_coords[nid].1;
        }
        let h_el = if ie < h_per_element.len() { h_per_element[ie] } else { h_default };
        let s_factor = if ie < stiffness_factors.len() { stiffness_factors[ie] } else { 1.0 };
        let ke = crate::plate_element::local_stiffness_matrix(&coords, e, nu, h_el);
        let ke_scaled = ke * s_factor;
        let dofs: [usize; 12] = std::array::from_fn(|i| {
            let ei = i / 3;
            3 * el[ei] + (i % 3)
        });
        for r in 0..12 {
            for c in 0..12 {
                let val = ke_scaled[(r, c)];
                if val.abs() > 1e-18 {
                    row_idx.push(dofs[r]);
                    col_idx.push(dofs[c]);
                    data_val.push(val);
                }
            }
        }
    }

    // --- Winkler springs ---
    for i in 0..n_nodes {
        let area = if i < tributary_areas.len() { tributary_areas[i] } else { 0.0 };
        if !opening_mask.is_empty() && i < opening_mask.len() && !opening_mask[i] {
            // Ghost node → penalty
            for d in 0..3 {
                row_idx.push(3 * i + d);
                col_idx.push(3 * i + d);
                data_val.push(penalty);
            }
        } else if i < active_springs.len() && active_springs[i] {
            let kv = if i < kv_nodal.len() { kv_nodal[i] } else { 0.0 };
            let k_spring = kv * area;
            if k_spring > 0.0 {
                row_idx.push(3 * i);
                col_idx.push(3 * i);
                data_val.push(k_spring);
            }
        }
    }

    // --- Discrete supports ---
    for s in 0..supp_x.len() {
        let (nodes4, weights4) = find_cell_weights(xs, ys, nx, supp_x[s], supp_y[s]);
        for (n, &w) in nodes4.iter().zip(weights4.iter()) {
            let kz = supp_kz[s] * w * w;
            row_idx.push(3 * n);
            col_idx.push(3 * n);
            data_val.push(kz);
            if s < supp_krx.len() && supp_krx[s] > 0.0 {
                row_idx.push(3 * n + 1);
                col_idx.push(3 * n + 1);
                data_val.push(supp_krx[s] * w * w);
            }
            if s < supp_kry.len() && supp_kry[s] > 0.0 {
                row_idx.push(3 * n + 2);
                col_idx.push(3 * n + 2);
                data_val.push(supp_kry[s] * w * w);
            }
        }
    }

    // --- Piles ---
    for p in 0..pile_x.len() {
        let (nodes4, weights4) = find_cell_weights(xs, ys, nx, pile_x[p], pile_y[p]);
        let k_pile = pile_k[p] * 1000.0;
        for (n, &w) in nodes4.iter().zip(weights4.iter()) {
            row_idx.push(3 * n);
            col_idx.push(3 * n);
            data_val.push(k_pile * w * w);
        }
    }

    // --- RHS: uniform load ---
    if q_uniform.abs() > 0.0 {
        for ie in 0..n_elements {
            if !opening_mask.is_empty() && ie < opening_mask.len() && opening_mask[ie] { continue; }
            let el = &elements[ie * 4..ie * 4 + 4];
            let xmin_el = el.iter().map(|&n| node_coords[n].0).fold(f64::MAX, f64::min);
            let xmax_el = el.iter().map(|&n| node_coords[n].0).fold(f64::MIN, f64::max);
            let ymin_el = el.iter().map(|&n| node_coords[n].1).fold(f64::MAX, f64::min);
            let ymax_el = el.iter().map(|&n| node_coords[n].1).fold(f64::MIN, f64::max);
            let a_el = (xmax_el - xmin_el) * (ymax_el - ymin_el);
            let fe = q_uniform * a_el / 4.0;
            distributed_load_total += q_uniform * a_el;
            for &n in el {
                rhs[3 * n] += fe;
            }
        }
    }

    // --- RHS: area loads ---
    for al in 0..area_load_xmin.len() {
        let al_q = area_load_q[al];
        if al_q == 0.0 { continue; }
        for ie in 0..n_elements {
            if !opening_mask.is_empty() && ie < opening_mask.len() && opening_mask[ie] { continue; }
            let el = &elements[ie * 4..ie * 4 + 4];
            let cx: f64 = el.iter().map(|&n| node_coords[n].0).sum::<f64>() / 4.0;
            let cy: f64 = el.iter().map(|&n| node_coords[n].1).sum::<f64>() / 4.0;
            if cx >= area_load_xmin[al] && cx <= area_load_xmax[al]
                && cy >= area_load_ymin[al] && cy <= area_load_ymax[al]
            {
                let xmin_el = el.iter().map(|&n| node_coords[n].0).fold(f64::MAX, f64::min);
                let xmax_el = el.iter().map(|&n| node_coords[n].0).fold(f64::MIN, f64::max);
                let ymin_el = el.iter().map(|&n| node_coords[n].1).fold(f64::MAX, f64::min);
                let ymax_el = el.iter().map(|&n| node_coords[n].1).fold(f64::MIN, f64::max);
                let a_el = (xmax_el - xmin_el) * (ymax_el - ymin_el);
                let fe = al_q * a_el / 4.0;
                distributed_load_total += al_q * a_el;
                for &n in el {
                    rhs[3 * n] += fe;
                }
            }
        }
    }

    // --- RHS: column loads ---
    for col_chunk in column_loads.chunks(5) {
        if col_chunk.len() < 3 { break; }
        let cx = col_chunk[0];
        let cy = col_chunk[1];
        let p = col_chunk[2];
        let mx = if col_chunk.len() > 3 { col_chunk[3] } else { 0.0 };
        let my = if col_chunk.len() > 4 { col_chunk[4] } else { 0.0 };

        let (nodes4, weights4) = find_cell_weights(xs, ys, nx, cx, cy);
        for (&n, &w) in nodes4.iter().zip(weights4.iter()) {
            let v_load = p * w;
            rhs[3 * n] += v_load;
            nodal_column_loads[n] += v_load;
            rhs[3 * n + 1] += mx * w;
            rhs[3 * n + 2] += my * w;
        }
        column_load_total += p;
    }

    (row_idx, col_idx, data_val, rhs, distributed_load_total, column_load_total, nodal_column_loads)
}

/// Resolve K * u = F a partir de triplets COO + RHS, usando faer sparse LU.
/// Retorna o vetor solução u (flat, comprimento ndof).
pub fn solve_sparse(
    row: &[usize],
    col: &[usize],
    val: &[f64],
    rhs: &[f64],
    regularization: f64,
) -> Vec<f64> {
    let ndof = rhs.len();
    let n_triplets = row.len();

    // Build triplets with regularization
    let mut triplets = Vec::with_capacity(n_triplets + ndof);
    for i in 0..n_triplets {
        triplets.push((row[i], col[i], val[i]));
    }
    for i in 0..ndof {
        triplets.push((i, i, regularization));
    }

    let k_csc = faer::sparse::SparseColMat::<usize, f64>::try_new_from_triplets(
        ndof, ndof, &triplets,
    ).expect("Sparse matrix construction failed");

    let f = Mat::<f64>::from_fn(ndof, 1, |i, _| rhs[i]);
    let lu = k_csc.sp_lu().expect("LU decomposition failed");
    let u = lu.solve(&f);

    let mut u_vec = vec![0.0; ndof];
    for i in 0..ndof {
        u_vec[i] = u[(i, 0)];
    }
    u_vec
}
