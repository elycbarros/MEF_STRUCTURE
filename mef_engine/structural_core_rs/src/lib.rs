use pyo3::prelude::*;
use pyo3::types::PyDict;
use serde::{Serialize, Deserialize};
use rayon::prelude::*;
pub use faer::prelude::*;
use faer::sparse::linalg::lu::SymbolicLu;
use faer::sparse::linalg::solvers::Lu;
use numpy::{PyArrayMethods, IntoPyArray};
use std::collections::HashMap;
pub mod plate_element;
pub mod beam_1d;
pub mod beam_3d;
pub mod frame_3d;
pub mod slab_mesh;
pub mod column_fiber;

use nalgebra as na;
use na::{DMatrix, DVector};
use crate::slab_mesh::{RustHole, RustPillar, SlabModel};

// ----------------------------
// Modelos de dados
// ----------------------------
#[derive(Debug, Clone, Serialize, Deserialize, FromPyObject)]
pub struct Node2D {
    pub id: i32,
    pub x: f64,
    pub y: f64,
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SlabMaterial {
    #[pyo3(get, set)]
    pub e: f64,
    #[pyo3(get, set)]
    pub nu: f64,
    #[pyo3(get, set)]
    pub h: f64,
}

#[pymethods]
impl SlabMaterial {
    #[new]
    pub fn new(e: f64, nu: f64, h: f64) -> Self {
        Self { e, nu, h }
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SlabElement {
    #[pyo3(get, set)]
    pub id: i32,
    #[pyo3(get, set)]
    pub nodes: [i32; 4],
}

#[pymethods]
impl SlabElement {
    #[new]
    pub fn new(id: i32, nodes: [i32; 4]) -> Self {
        Self { id, nodes }
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Node3D {
    #[pyo3(get, set)]
    pub id: i32,
    #[pyo3(get, set)]
    pub x: f64,
    #[pyo3(get, set)]
    pub y: f64,
    #[pyo3(get, set)]
    pub z: f64,
}

#[pymethods]
impl Node3D {
    #[new]
    pub fn new(id: i32, x: f64, y: f64, z: f64) -> Self {
        Self { id, x, y, z }
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Frame3DModel {
    #[pyo3(get, set)]
    pub nodes: Vec<Node3D>,
    #[pyo3(get, set)]
    pub members: Vec<Frame3DMemberPy>,
    #[pyo3(get, set)]
    pub loads: Vec<Frame3DLoadPy>,
    #[pyo3(get, set)]
    pub fixed_dofs: Vec<usize>,
    #[pyo3(get, set)]
    pub reduce_stiffness: bool,
}

#[pymethods]
impl Frame3DModel {
    #[new]
    pub fn new(nodes: Vec<Node3D>, members: Vec<Frame3DMemberPy>, loads: Vec<Frame3DLoadPy>, fixed_dofs: Vec<usize>, reduce_stiffness: bool) -> Self {
        Self { nodes, members, loads, fixed_dofs, reduce_stiffness }
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Frame3DMemberPy {
    #[pyo3(get, set)]
    pub id: i32,
    #[pyo3(get, set)]
    pub node_i: i32,
    #[pyo3(get, set)]
    pub node_j: i32,
    #[pyo3(get, set)]
    pub e: f64,
    #[pyo3(get, set)]
    pub g: f64,
    #[pyo3(get, set)]
    pub area: f64,
    #[pyo3(get, set)]
    pub iy: f64,
    #[pyo3(get, set)]
    pub iz: f64,
    #[pyo3(get, set)]
    pub j: f64,
    #[pyo3(get, set)]
    pub member_type: i32,
}

#[pymethods]
impl Frame3DMemberPy {
    #[new]
    pub fn new(id: i32, node_i: i32, node_j: i32, e: f64, g: f64, area: f64, iy: f64, iz: f64, j: f64, member_type: i32) -> Self {
        Self { id, node_i, node_j, e, g, area, iy, iz, j, member_type }
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Frame3DLoadPy {
    #[pyo3(get, set)]
    pub node_id: i32,
    #[pyo3(get, set)]
    pub fx: f64,
    #[pyo3(get, set)]
    pub fy: f64,
    #[pyo3(get, set)]
    pub fz: f64,
    #[pyo3(get, set)]
    pub mx: f64,
    #[pyo3(get, set)]
    pub my: f64,
    #[pyo3(get, set)]
    pub mz: f64,
}

#[pymethods]
impl Frame3DLoadPy {
    #[new]
    pub fn new(node_id: i32, fx: f64, fy: f64, fz: f64, mx: f64, my: f64, mz: f64) -> Self {
        Self { node_id, fx, fy, fz, mx, my, mz }
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Beam1DModel {
    #[pyo3(get, set)]
    pub l: f64,
    #[pyo3(get, set)]
    pub n_elements: usize,
    #[pyo3(get, set)]
    pub e: f64,
    #[pyo3(get, set)]
    pub g: f64,
    #[pyo3(get, set)]
    pub i: f64,
    #[pyo3(get, set)]
    pub j: f64,
    #[pyo3(get, set)]
    pub supports: Vec<Beam1DSupportPy>,
    #[pyo3(get, set)]
    pub point_loads: Vec<Beam1DPointLoadPy>,
    #[pyo3(get, set)]
    pub distributed_loads: Vec<Beam1DDistLoadPy>,
    #[pyo3(get, set)]
    pub offset: f64,
}

#[pymethods]
impl Beam1DModel {
    #[new]
    pub fn new(l: f64, n_elements: usize, e: f64, g: f64, i: f64, j: f64, supports: Vec<Beam1DSupportPy>, point_loads: Vec<Beam1DPointLoadPy>, distributed_loads: Vec<Beam1DDistLoadPy>, offset: f64) -> Self {
        Self { l, n_elements, e, g, i, j, supports, point_loads, distributed_loads, offset }
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Beam1DSupportPy {
    #[pyo3(get, set)]
    pub x: f64,
    #[pyo3(get, set)]
    pub k_w: f64,
    #[pyo3(get, set)]
    pub k_theta: f64,
    #[pyo3(get, set)]
    pub k_phi: f64,
}

#[pymethods]
impl Beam1DSupportPy {
    #[new]
    pub fn new(x: f64, k_w: f64, k_theta: f64, k_phi: f64) -> Self {
        Self { x, k_w, k_theta, k_phi }
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Beam1DPointLoadPy {
    #[pyo3(get, set)]
    pub x: f64,
    #[pyo3(get, set)]
    pub p: f64,
    #[pyo3(get, set)]
    pub m: f64,
    #[pyo3(get, set)]
    pub eccentricity: f64,
}

#[pymethods]
impl Beam1DPointLoadPy {
    #[new]
    pub fn new(x: f64, p: f64, m: f64, eccentricity: f64) -> Self {
        Self { x, p, m, eccentricity }
    }
}

#[pyclass]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Beam1DDistLoadPy {
    #[pyo3(get, set)]
    pub x_start: f64,
    #[pyo3(get, set)]
    pub x_end: f64,
    #[pyo3(get, set)]
    pub q_start: f64,
    #[pyo3(get, set)]
    pub q_end: f64,
    #[pyo3(get, set)]
    pub eccentricity: f64,
}

#[pymethods]
impl Beam1DDistLoadPy {
    #[new]
    pub fn new(x_start: f64, x_end: f64, q_start: f64, q_end: f64, eccentricity: f64) -> Self {
        Self { x_start, x_end, q_start, q_end, eccentricity }
    }
}

#[pyfunction]
#[pyo3(signature = (nodes, elements, material, nodal_loads, fixed_dofs))]
pub fn solve_slabs(
    py: Python,
    nodes: Vec<Node2D>,
    elements: Vec<SlabElement>,
    material: SlabMaterial,
    nodal_loads: Vec<f64>,
    fixed_dofs: Vec<usize>,
) -> PyResult<PyObject> {
    let n_nodes = nodes.len();
    let n_dofs = n_nodes * 3;
    let mut rhs = vec![0.0; n_dofs];
    for (i, &val) in nodal_loads.iter().enumerate() {
        if i < n_dofs {
            rhs[i] = val;
        }
    }
    
    let mut node_map = HashMap::new();
    for (i, n) in nodes.iter().enumerate() {
        node_map.insert(n.id, i);
    }
    
    let mut entries = Vec::new();
    let material_ref = &material;

    for element in &elements {
        let n_indices: Vec<usize> = element.nodes.iter().map(|&id| *node_map.get(&id).unwrap()).collect();
        let mut coords = na::Matrix4x2::zeros();
        for i in 0..4 {
            let idx = n_indices[i];
            coords[(i, 0)] = nodes[idx].x;
            coords[(i, 1)] = nodes[idx].y;
        }
        
        let ke = plate_element::local_stiffness_matrix(&coords, material_ref.e, material_ref.nu, material_ref.h);
        
        let mut dofs = Vec::with_capacity(12);
        for &idx in &n_indices {
            dofs.push(idx * 3);
            dofs.push(idx * 3 + 1);
            dofs.push(idx * 3 + 2);
        }
        
        for r in 0..12 {
            for c in 0..12 {
                let val = ke[(r, c)];
                if val.abs() > 1e-15 {
                    entries.push((dofs[r], dofs[c], val));
                }
            }
        }
    }
    
    let penalty = 1e20;
    for &dof in &fixed_dofs {
        if dof < n_dofs {
            entries.push((dof, dof, penalty));
            rhs[dof] = 0.0;
        }
    }
    
    let k_csc = faer::sparse::SparseColMat::<usize, f64>::try_new_from_triplets(n_dofs, n_dofs, &entries)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("CSC build failed: {:?}", e)))?;
    
    let f = Mat::<f64>::from_fn(n_dofs, 1, |i, _| rhs[i]);
    let lu = k_csc.sp_lu().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("LU failed: {:?}", e)))?;
    let u = lu.solve(&f);
    
    let mut u_vec = vec![0.0; n_dofs];
    for i in 0..n_dofs { u_vec[i] = u[(i, 0)]; }

    let u_rs = nalgebra::DVector::from_vec(u_vec.clone());
    
    let element_results: Vec<((f64, f64, f64, f64, f64), Vec<(usize, f64)>)> = elements.par_iter().map(|element| {
        let n_indices: Vec<usize> = element.nodes.iter().map(|&id| *node_map.get(&id).unwrap()).collect();
        let mut coords = na::Matrix4x2::zeros();
        for i in 0..4 {
            let idx = n_indices[i];
            coords[(i, 0)] = nodes[idx].x;
            coords[(i, 1)] = nodes[idx].y;
        }
        let ke = plate_element::local_stiffness_matrix(&coords, material_ref.e, material_ref.nu, material_ref.h);
        
        let mut u_el_vec = Vec::with_capacity(12);
        let mut dofs = Vec::with_capacity(12);
        for &idx in &n_indices {
            let d = idx * 3;
            u_el_vec.push(u_rs[d]);
            u_el_vec.push(u_rs[d + 1]);
            u_el_vec.push(u_rs[d + 2]);
            dofs.push(d);
            dofs.push(d + 1);
            dofs.push(d + 2);
        }
        let u_el = nalgebra::DVector::from_vec(u_el_vec);
        let efforts = plate_element::compute_efforts(&coords, &u_el, material_ref.e, material_ref.nu, material_ref.h);
        let fe_vec = nalgebra::DVector::zeros(12);
        let r_el = fe_vec - (&ke * &u_el);
        let mut local_reactions = Vec::with_capacity(12);
        for i in 0..12 {
            local_reactions.push((dofs[i], r_el[i]));
        }
        (efforts, local_reactions)
    }).collect();

    let mut mx = Vec::new();
    let mut my = Vec::new();
    let mut mxy = Vec::new();
    let mut vx = Vec::new();
    let mut vy = Vec::new();
    let mut reactions = vec![0.0; n_dofs];

    for (eff, local_r) in element_results {
        mx.push(eff.0);
        my.push(eff.1);
        mxy.push(eff.2);
        vx.push(eff.3);
        vy.push(eff.4);
        for (dof, val) in local_r {
            reactions[dof] += val;
        }
    }

    let dict = PyDict::new_bound(py);
    dict.set_item("u", u_vec.into_pyarray_bound(py))?;
    dict.set_item("mx", mx.into_pyarray_bound(py))?;
    dict.set_item("my", my.into_pyarray_bound(py))?;
    dict.set_item("mxy", mxy.into_pyarray_bound(py))?;
    dict.set_item("vx", vx.into_pyarray_bound(py))?;
    dict.set_item("vy", vy.into_pyarray_bound(py))?;
    dict.set_item("reactions", reactions.into_pyarray_bound(py))?;
    Ok(dict.to_object(py))
}

#[pyfunction]
pub fn solve_slabs_from_model(
    py: Python,
    model: SlabModel,
    material: SlabMaterial,
) -> PyResult<PyObject> {
    let mesh = slab_mesh::generate_mesh(&model);
    let internal_nodes: Vec<Node2D> = mesh.nodes.iter().enumerate().map(|(i, &(x, y))| {
        Node2D { id: i as i32, x, y }
    }).collect();
    let internal_elements: Vec<SlabElement> = mesh.elements.iter().enumerate().map(|(i, &nodes)| {
        SlabElement { id: i as i32, nodes: [nodes[0] as i32, nodes[1] as i32, nodes[2] as i32, nodes[3] as i32] }
    }).collect();
    let mut fixed_dofs = Vec::new();
    for &node_idx in &mesh.support_nodes {
        fixed_dofs.push(node_idx * 3);
    }
    let results = solve_slabs(py, internal_nodes, internal_elements, material, mesh.nodal_loads, fixed_dofs)?;
    let dict: Bound<'_, PyDict> = results.downcast_bound(py)?.clone();
    dict.set_item("nodes", mesh.nodes)?;
    dict.set_item("elements", mesh.elements)?;
    Ok(dict.to_object(py))
}

#[pyfunction]
pub fn solve_frame_3d_from_model(
    py: Python,
    model: Frame3DModel,
) -> PyResult<PyObject> {
    let n_nodes = model.nodes.len();
    let n_dofs = n_nodes * 6;
    let mut rhs = vec![0.0; n_dofs];
    let mut node_index = HashMap::new();
    for (i, n) in model.nodes.iter().enumerate() {
        node_index.insert(n.id, i);
    }
    for load in &model.loads {
        if let Some(&idx) = node_index.get(&load.node_id) {
            rhs[idx * 6] += load.fx;
            rhs[idx * 6 + 1] += load.fy;
            rhs[idx * 6 + 2] += load.fz;
            rhs[idx * 6 + 3] += load.mx;
            rhs[idx * 6 + 4] += load.my;
            rhs[idx * 6 + 5] += load.mz;
        }
    }
    let mut entries = Vec::new();
    let node_map: HashMap<i32, (f64, f64, f64)> = model.nodes.iter().map(|n| (n.id, (n.x, n.y, n.z))).collect();
    for member in &model.members {
        let n1_coords = node_map.get(&member.node_i).expect("Node I not found");
        let n2_coords = node_map.get(&member.node_j).expect("Node J not found");
        let dx = n2_coords.0 - n1_coords.0;
        let dy = n2_coords.1 - n1_coords.1;
        let dz = n2_coords.2 - n1_coords.2;
        let l = (dx * dx + dy * dy + dz * dz).sqrt();
        let rust_member = crate::frame_3d::Frame3DMember {
            id: member.id,
            node_i: *node_index.get(&member.node_i).unwrap(),
            node_j: *node_index.get(&member.node_j).unwrap(),
            e: member.e, g: member.g, area: member.area, iy: member.iy, iz: member.iz, j: member.j, l,
        };
        let t = crate::frame_3d::get_transformation_matrix(*n1_coords, *n2_coords);
        let mut k_local = crate::frame_3d::get_stiffness_matrix(&rust_member, 0.0);
        if model.reduce_stiffness {
            let factor = if member.member_type == 0 { 0.8 } else { 0.4 };
            k_local *= factor;
        }
        let k_global = t.transpose() * k_local * t;
        let i_idx = rust_member.node_i;
        let j_idx = rust_member.node_j;
        let dofs = [
            i_idx * 6, i_idx * 6 + 1, i_idx * 6 + 2, i_idx * 6 + 3, i_idx * 6 + 4, i_idx * 6 + 5,
            j_idx * 6, j_idx * 6 + 1, j_idx * 6 + 2, j_idx * 6 + 3, j_idx * 6 + 4, j_idx * 6 + 5,
        ];
        for r in 0..12 {
            for c in 0..12 {
                let val = k_global[(r, c)];
                if val.abs() > 1e-15 {
                    entries.push((dofs[r], dofs[c], val));
                }
            }
        }
    }
    let penalty = 1e20;
    for &dof in &model.fixed_dofs {
        if dof < n_dofs {
            entries.push((dof, dof, penalty));
            rhs[dof] = 0.0;
        }
    }
    let k_csc = faer::sparse::SparseColMat::<usize, f64>::try_new_from_triplets(n_dofs, n_dofs, &entries)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("CSC build failed: {:?}", e)))?;
    let f = Mat::<f64>::from_fn(n_dofs, 1, |i, _| rhs[i]);
    let lu = k_csc.sp_lu().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("LU failed: {:?}", e)))?;
    let u = lu.solve(&f);
    let mut u_vec = vec![0.0; n_dofs];
    for i in 0..n_dofs { u_vec[i] = u[(i, 0)]; }
    
    let proofs = PyDict::new_bound(py);
    if let Some(m) = model.members.first() {
        let n1 = node_map.get(&m.node_i).unwrap();
        let n2 = node_map.get(&m.node_j).unwrap();
        let dx = n2.0 - n1.0; let dy = n2.1 - n1.1; let dz = n2.2 - n1.2;
        let l = (dx*dx + dy*dy + dz*dz).sqrt();
        let rust_m = crate::frame_3d::Frame3DMember {
            id: m.id, node_i: 0, node_j: 1,
            e: m.e, g: m.g, area: m.area, iy: m.iy, iz: m.iz, j: m.j, l,
        };
        let t = crate::frame_3d::get_transformation_matrix(*n1, *n2);
        let k_loc = crate::frame_3d::get_stiffness_matrix(&rust_m, 0.0);
        let mut k_flat = Vec::with_capacity(144);
        for r in 0..12 { for c in 0..12 { k_flat.push(k_loc[(r,c)]); } }
        let mut t_flat = Vec::with_capacity(144);
        for r in 0..12 { for c in 0..12 { t_flat.push(t[(r,c)]); } }
        proofs.set_item("sample_member_id", m.id)?;
        proofs.set_item("sample_k_local", k_flat)?;
        proofs.set_item("sample_t_matrix", t_flat)?;
        proofs.set_item("sample_l", l)?;
    }

    let dict = PyDict::new_bound(py);
    dict.set_item("u", u_vec.into_pyarray_bound(py))?;
    dict.set_item("pedagogical_proofs", proofs)?;
    Ok(dict.to_object(py))
}

#[pyfunction]
pub fn solve_beams_from_model(
    py: Python,
    model: Beam1DModel,
) -> PyResult<PyObject> {
    let l = model.l;
    let n_elem = model.n_elements;
    let n_nodes = n_elem + 1;
    let n_dofs = n_nodes * 3;
    let dx = l / n_elem as f64;
    let mut rhs = vec![0.0; n_dofs];
    let mut entries = Vec::new();
    for i in 0..n_elem {
        let ke = crate::beam_1d::get_stiffness_matrix_raw(dx, model.e, model.g, model.i, model.j);
        let dofs = [i * 3, i * 3 + 1, i * 3 + 2, (i + 1) * 3, (i + 1) * 3 + 1, (i + 1) * 3 + 2];
        for r in 0..6 {
            for c in 0..6 {
                let val = ke[(r, c)];
                if val.abs() > 1e-15 {
                    entries.push((dofs[r], dofs[c], val));
                }
            }
        }
    }
    for load in &model.distributed_loads {
        let q_avg = (load.q_start + load.q_end) / 2.0;
        let fe = crate::beam_1d::get_load_vector_raw(load.x_end - load.x_start, q_avg, load.eccentricity + model.offset);
        let start_node = (load.x_start / dx).round() as usize;
        let end_node = (load.x_end / dx).round() as usize;
        for i in start_node..end_node {
            let dofs = [i * 3, i * 3 + 1, i * 3 + 2, (i + 1) * 3, (i + 1) * 3 + 1, (i + 1) * 3 + 2];
            for k in 0..6 { rhs[dofs[k]] += fe[k]; }
        }
    }
    for load in &model.point_loads {
        let node_idx = (load.x / dx).round() as usize;
        if node_idx < n_nodes {
            rhs[node_idx * 3] -= load.p;
            rhs[node_idx * 3 + 1] += load.m;
            rhs[node_idx * 3 + 2] += load.p * (load.eccentricity + model.offset);
        }
    }
    let penalty = 1e20;
    for support in &model.supports {
        let node_idx = (support.x / dx).round() as usize;
        if node_idx < n_nodes {
            if support.k_w > 0.0 { entries.push((node_idx * 3, node_idx * 3, support.k_w * penalty)); }
            if support.k_theta > 0.0 { entries.push((node_idx * 3 + 1, node_idx * 3 + 1, support.k_theta * penalty)); }
            if support.k_phi > 0.0 { entries.push((node_idx * 3 + 2, node_idx * 3 + 2, support.k_phi * penalty)); }
        }
    }
    let k_csc = faer::sparse::SparseColMat::<usize, f64>::try_new_from_triplets(n_dofs, n_dofs, &entries)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(format!("CSC build failed: {:?}", e)))?;
    let f = Mat::<f64>::from_fn(n_dofs, 1, |i, _| rhs[i]);
    let lu = k_csc.sp_lu().map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(format!("LU failed: {:?}", e)))?;
    let u = lu.solve(&f);
    let mut u_vec = vec![0.0; n_dofs];
    for i in 0..n_dofs { u_vec[i] = u[(i, 0)]; }
    
    let proofs = PyDict::new_bound(py);
    // Sample first element
    let ke = crate::beam_1d::get_stiffness_matrix_raw(dx, model.e, model.g, model.i, model.j);
    let mut ke_flat = Vec::with_capacity(36);
    for r in 0..6 { for c in 0..6 { ke_flat.push(ke[(r,c)]); } }
    proofs.set_item("sample_k_local", ke_flat)?;
    proofs.set_item("sample_dx", dx)?;

    let dict = PyDict::new_bound(py);
    dict.set_item("u", u_vec.into_pyarray_bound(py))?;
    dict.set_item("pedagogical_proofs", proofs)?;
    Ok(dict.to_object(py))
}

#[pyfunction]
pub fn solve_column_fiber(
    model: column_fiber::ColumnFiberModel,
    target_n: f64,
    target_mx: f64,
    target_my: f64,
) -> PyResult<(f64, f64, f64, bool)> {
    Ok(column_fiber::solve_equilibrium(&model, target_n, target_mx, target_my))
}

#[pyfunction]
pub fn get_column_interaction_envelope(
    model: column_fiber::ColumnFiberModel,
    axis: String,
) -> PyResult<Vec<(f64, f64)>> {
    let a = axis.chars().next().unwrap_or('x');
    Ok(column_fiber::generate_interaction_envelope(&model, a))
}

#[pymodule]
fn structural_core_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<RustHole>()?;
    m.add_class::<RustPillar>()?;
    m.add_class::<SlabModel>()?;
    m.add_class::<SlabMaterial>()?;
    m.add_class::<SlabElement>()?;
    m.add_function(wrap_pyfunction!(solve_slabs, m)?)?;
    m.add_function(wrap_pyfunction!(solve_slabs_from_model, m)?)?;
    m.add_function(wrap_pyfunction!(solve_frame_3d_from_model, m)?)?;
    m.add_function(wrap_pyfunction!(solve_beams_from_model, m)?)?;
    m.add_class::<Frame3DModel>()?;
    m.add_class::<Frame3DMemberPy>()?;
    m.add_class::<Frame3DLoadPy>()?;
    m.add_class::<Beam1DModel>()?;
    m.add_class::<Beam1DSupportPy>()?;
    m.add_class::<Beam1DPointLoadPy>()?;
    m.add_class::<Beam1DDistLoadPy>()?;
    m.add_class::<Node3D>()?;
    m.add_class::<column_fiber::ColumnFiberModel>()?;
    m.add_function(wrap_pyfunction!(solve_column_fiber, m)?)?;
    m.add_function(wrap_pyfunction!(get_column_interaction_envelope, m)?)?;
    Ok(())
}
