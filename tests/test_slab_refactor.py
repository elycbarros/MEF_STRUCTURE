import unittest
import numpy as np
from mef_engine.slab_design_engine import SlabDesignEngine, SlabDesignConfig
from mef_engine.slab_serviceability import SlabServiceabilityEngine, ServiceabilityConfig

class TestSlabRefactor(unittest.TestCase):
    def test_flexure_nbr6118_2023(self):
        engine = SlabDesignEngine()
        cfg = SlabDesignConfig(fck=30, h=0.20, cover=0.03, bar_diameter_mm=10.0)
        
        # Momento Md = 50 kNm/m
        res = engine.calculate_flexure_section(50.0, cfg)
        
        # Verificações básicas
        self.assertGreater(res['as_req_cm2'], 0)
        self.assertTrue(res['is_ductile'])
        self.assertGreaterEqual(res['as_final_cm2'], res['as_min_cm2'])
        
        # Teste de fck alto (> 50 MPa)
        cfg_high = SlabDesignConfig(fck=60, h=0.20)
        res_high = engine.calculate_flexure_section(50.0, cfg_high)
        self.assertIn('z_m', res_high)

    def test_punching_2023_k_factor(self):
        engine = SlabDesignEngine()
        cfg = SlabDesignConfig(fck=25, h=0.20, cover=0.03)
        d = 0.165 # h - cover - phi/2
        
        # Teste com d pequeno para forçar k > 2.0 (deve ser limitado a 2.0)
        # k = 1 + sqrt(200/165) = 1 + 1.1 = 2.1 (deve limitar a 2.0)
        res = engine.check_punching_2023(200.0, (0,0), 1.0, 3.0, d, 0.01, cfg)
        self.assertEqual(res['k_factor'], 2.0)

    def test_branson_inertia(self):
        engine = SlabServiceabilityEngine()
        cfg = ServiceabilityConfig(fck=30, h=0.15)
        
        # Caso 1: Momento baixo (não fissurado) -> Ie = Ic
        res_low = engine.calculate_branson_inertia(1.0, 5.0, cfg)
        self.assertAlmostEqual(res_low['reduction_factor'], 1.0)
        
        # Caso 2: Momento alto (fissurado) -> Ie < Ic
        res_high = engine.calculate_branson_inertia(20.0, 5.0, cfg)
        self.assertLess(res_high['reduction_factor'], 1.0)
        self.assertGreater(res_high['reduction_factor'], 0.1) # razoável

if __name__ == '__main__':
    unittest.main()
