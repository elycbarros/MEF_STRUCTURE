use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_assemble_13x13(c: &mut Criterion) {
    let nx = 13;
    let ny = 13;
    let nn = nx * ny;

    let nodes_xy: Vec<f64> = (0..nn)
        .flat_map(|i| {
            let x = (i % nx) as f64 * 24.0 / (nx - 1) as f64;
            let y = (i / nx) as f64 * 24.0 / (ny - 1) as f64;
            [x, y]
        })
        .collect();
    let elements: Vec<usize> = (0..(nx - 1) * (ny - 1))
        .flat_map(|ei| {
            let j = ei / (nx - 1);
            let i = ei % (nx - 1);
            let n0 = j * nx + i;
            [n0, n0 + 1, n0 + nx + 1, n0 + nx]
        })
        .collect();
    let tributary_areas: Vec<f64> = (0..nn).map(|_| 2.0 * 2.0).collect();
    let xs: Vec<f64> = (0..nx).map(|i| i as f64 * 24.0 / (nx - 1) as f64).collect();
    let ys: Vec<f64> = (0..ny).map(|j| j as f64 * 24.0 / (ny - 1) as f64).collect();
    let n_elems = elements.len() / 4;
    let h_per_el: Vec<f64> = (0..n_elems).map(|_| 0.6).collect();
    let stf: Vec<f64> = (0..n_elems).map(|_| 1.0).collect();

    let kv: Vec<f64> = (0..nn).map(|_| 40e6).collect();
    let active: Vec<bool> = (0..nn).map(|_| true).collect();

    // column loads
    let col: Vec<f64> = vec![4.0, 4.0, 2000e3, 0.0, 0.0];

    let penalty = 1e20;

    c.bench_function("assemble_radier_13x13", |b| {
        b.iter(|| {
            let _res = structural_core_rs::radier_winkler::assemble_system(
                black_box(&nodes_xy),
                black_box(&elements),
                black_box(&tributary_areas),
                black_box(&xs),
                black_box(&ys),
                black_box(nx),
                black_box(&stf),
                black_box(&h_per_el),
                black_box(&[]), // opening_mask
                black_box(&kv),
                black_box(&active),
                black_box(32e9),
                black_box(0.2),
                black_box(0.6),
                black_box(30000.0),
                black_box(&col),
                black_box(&[]), // area loads
                black_box(&[]),
                black_box(&[]),
                black_box(&[]),
                black_box(&[]),
                black_box(&[]), // supports
                black_box(&[]),
                black_box(&[]),
                black_box(&[]),
                black_box(&[]),
                black_box(&[]), // piles
                black_box(&[]),
                black_box(&[]),
                black_box(penalty),
            );
        })
    });
}

criterion_group!(benches, bench_assemble_13x13);
criterion_main!(benches);
