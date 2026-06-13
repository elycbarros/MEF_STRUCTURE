print('Testing Structural Core RS...')

# Test Frame3DModel
try:
    from structural_core_rs import Frame3DMemberPy, Frame3DModel, Node3D, solve_frame_3d_from_model

    nodes = [Node3D(0, 0.0, 0.0, 0.0), Node3D(1, 0.0, 0.0, 3.0)]
    members = [Frame3DMemberPy(0, 0, 1, 2.1e11, 8.0e10, 0.01, 0.0001, 0.0001, 0.0002, 1)]
    loads = []  # No loads
    fixed_dofs = [0, 1, 2, 3, 4, 5]  # Fixed at base (Node 0)
    model = Frame3DModel(nodes, members, loads, fixed_dofs, False)
    res = solve_frame_3d_from_model(model)
    print('Frame3D Solve Success!')
except Exception as e:
    import traceback

    print(f'Frame3D Solve Failed: {e}')
    traceback.print_exc()

# Test Beam1DModel
try:
    from structural_core_rs import Beam1DModel, Beam1DSupportPy, solve_beams_from_model

    supports = [Beam1DSupportPy(0.0, 1.0, 1.0, 1.0), Beam1DSupportPy(5.0, 1.0, 0.0, 0.0)]
    model = Beam1DModel(5.0, 10, 2.1e11, 8.0e10, 0.0001, 0.0001, supports, [], [], 0.0)
    res = solve_beams_from_model(model)
    print('Beam1D Solve Success!')
except Exception as e:
    print(f'Beam1D Solve Failed: {e}')

print('Verification Complete.')
