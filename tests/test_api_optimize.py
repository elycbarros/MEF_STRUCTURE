import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mef_engine'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from api import app
from fastapi.testclient import TestClient


class TestOptimizeAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_optimize_design_radier(self):
        payload = {
            'current_h': 0.30,
            'target_sigma': 150.0,
            'config': {
                'Lx': 5.0,
                'Ly': 5.0,
                'h': 0.30,
                'kv': 15.0e6,
                'q': 80.0e3,
                'sigma_adm_kPa': 150.0,
                'fck': 30.0,
                'fyk': 500.0,
                'system_type': 'radier',
            },
        }
        response = self.client.post('/api/mestre/optimize_design', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('suggested_h', data)
        self.assertIn('suggested_fck', data)
        self.assertIn('estimated_cost_brl', data)
        self.assertIn('max_displacement_mm', data)

    def test_optimize_design_laje(self):
        payload = {
            'current_h': 0.12,
            'target_sigma': 0.0,  # Não se aplica a lajes diretamente
            'config': {
                'Lx': 4.0,
                'Ly': 4.0,
                'h': 0.12,
                'kv': 20.0e6,
                'q': 5.0e3,
                'fck': 25.0,
                'fyk': 500.0,
                'system_type': 'laje',
                'slab_type': 'solid',
                'pillars': [
                    {'id': 'P1', 'x': 0.1, 'y': 0.1, 'p_kN': 100.0},
                    {'id': 'P2', 'x': 3.9, 'y': 0.1, 'p_kN': 100.0},
                    {'id': 'P3', 'x': 3.9, 'y': 3.9, 'p_kN': 100.0},
                    {'id': 'P4', 'x': 0.1, 'y': 3.9, 'p_kN': 100.0},
                ],
            },
        }
        response = self.client.post('/api/mestre/optimize_design', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('suggested_h', data)
        self.assertIn('suggested_fck', data)
        self.assertIn('estimated_cost_brl', data)

    def test_optimize_design_reliability(self):
        payload = {
            'current_h': 0.30,
            'target_sigma': 300.0,
            'enable_reliability_mode': True,
            'target_reliability_beta': 2.5,
            'kv_cov': 0.15,
            'q_cov': 0.08,
            'config': {
                'Lx': 5.0,
                'Ly': 5.0,
                'h': 0.30,
                'kv': 15.0e6,
                'q': 20.0e3,
                'sigma_adm_kPa': 300.0,
                'fck': 30.0,
                'fyk': 500.0,
                'system_type': 'radier',
                'pillars': [
                    {'id': 'P1', 'x': 1.0, 'y': 1.0, 'p_kN': 50.0},
                    {'id': 'P2', 'x': 4.0, 'y': 1.0, 'p_kN': 50.0},
                    {'id': 'P3', 'x': 4.0, 'y': 4.0, 'p_kN': 50.0},
                    {'id': 'P4', 'x': 1.0, 'y': 4.0, 'p_kN': 50.0},
                ],
            },
        }
        response = self.client.post('/api/mestre/optimize_design', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('suggested_h', data)
        self.assertIn('suggested_fck', data)
        self.assertIn('reliability_index_beta', data)
        self.assertIn('failure_probability', data)
        # Deve retornar o índice obtido maior ou igual a zero
        self.assertGreaterEqual(data['reliability_index_beta'], 0.0)


if __name__ == '__main__':
    unittest.main()
