BASE_URL = 'http://localhost:8000'


def test_frame_analyze():
    # Mock data typical of a pedagogical frame
    payload = {
        'nodes': [
            {'id': 1, 'x': 0.0, 'y': 0.0, 'z': 0.0, 'extra': 'fails_here'},
            {'id': 2, 'x': 0.0, 'y': 0.0, 'z': 3.0},
        ],
        'members': [{'id': 1, 'node_i': 1, 'node_j': 2, 'section': {'b': 0.2, 'h': 0.5, 'E': 2.5e10}}],
        'loads': [{'node_id': 2, 'Fx': 10.0, 'Fy': 0.0, 'Fz': 0.0, 'Mx': 0.0, 'My': 0.0, 'Mz': 0.0}],
        'supports': {'1': [0, 1, 2, 3, 4, 5]},
        'show_matrix_proof': True,
    }

    try:
        # Note: We need to make sure the server is running.
        # But here I can just try to import and call the function directly to test logic.
        from routes.mestre_frame import MestreFrameRequest, analyze_mestre_frame

        req = MestreFrameRequest(**payload)
        import asyncio

        res = asyncio.run(analyze_mestre_frame(req))
        print('Success:', res['success'])
        print('Steps Count:', len(res.get('pedagogical_steps', [])))
        if res.get('pedagogical_steps'):
            print('First Step Title:', res['pedagogical_steps'][0]['title'])
    except Exception as e:
        print('Crashed with:', type(e).__name__, ':', str(e))


if __name__ == '__main__':
    test_frame_analyze()
