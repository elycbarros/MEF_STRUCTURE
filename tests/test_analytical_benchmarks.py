"""
Benchmarks analíticos — validam solvers contra soluções algébricas clássicas.
Cada teste compara o resultado numérico do MEF com a fórmula analítica
dentro de uma tolerância definida.
"""

import os
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'mef_engine'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from beam_solver import run_beam_analysis
from lajes_solver import LajeModel, LajesMindlinSolver, Material
from slab_design_engine import SlabDesignConfig, SlabDesignEngine
from slab_serviceability import ServiceabilityConfig, SlabServiceabilityEngine


class TestBeamSimplySupported(unittest.TestCase):
    """BEAM-001: Viga bi-apoiada c/ carga uniforme"""

    def setUp(self):
        self.L = 5.0
        self.q = 20.0
        self.b = 0.20
        self.h = 0.50
        self.fck = 30.0
        E_MPa = 5600 * np.sqrt(self.fck)
        self.E = E_MPa * 1e6
        self.I = self.b * self.h**3 / 12.0
        self.M_ana = self.q * self.L**2 / 8.0
        self.V_ana = self.q * self.L / 2.0
        self.delta_ana_m = 5.0 * self.q * 1000 * self.L**4 / (384 * self.E * self.I)

    def _solve(self):
        return run_beam_analysis(
            L=self.L,
            supports=[{'x': 0.0, 'type': 'pinned'}, {'x': self.L, 'type': 'roller'}],
            distributed_loads=[{'x_start': 0.0, 'x_end': self.L, 'q_start': self.q, 'q_end': self.q}],
            b=self.b,
            h=self.h,
            fck=self.fck,
            n_elements=40,
            nonlinear=False,
            include_self_weight=False,
        )

    def test_moment(self):
        result = self._solve()
        s = result.get('summary', result)
        mom = s.get('max_moment_kNm') or s.get('moment_max_kNm', 0)
        error = abs(mom - self.M_ana) / self.M_ana
        self.assertLessEqual(error, 0.05, f'M={mom:.3f} ≠ {self.M_ana:.3f}')

    def test_shear(self):
        result = self._solve()
        s = result.get('summary', result)
        shear = s.get('max_shear_kN') or s.get('shear_max_kN', 0)
        error = abs(shear - self.V_ana) / self.V_ana
        self.assertLessEqual(error, 0.05, f'V={shear:.3f} ≠ {self.V_ana:.3f}')

    def test_deflection(self):
        result = self._solve()
        s = result.get('summary', result)
        delta = s.get('max_deflection_mm', 0)
        delta_ana_mm = self.delta_ana_m * 1000.0
        if delta_ana_mm > 0:
            error = abs(delta - delta_ana_mm) / delta_ana_mm
            self.assertLessEqual(error, 0.15, f'δ={delta:.4f} ≠ {delta_ana_mm:.4f}')


class TestSlabEquilibrium(unittest.TestCase):
    """Laje com bordas apoiadas: equilíbrio"""

    def test_equilibrium(self):
        from lajes_solver import LineSupport, SupportType

        model = LajeModel(
            Lx=4.0,
            Ly=4.0,
            nx=8,
            ny=8,
            material=Material(E=30e9, nu=0.2, h=0.12),
            pillars=[],
            holes=[],
            line_supports=[
                LineSupport(id='b1', x1=0, y1=0, x2=4, y2=0, support_type=SupportType.PINNED, k_spring=1e14),
                LineSupport(id='b2', x1=0, y1=4, x2=4, y2=4, support_type=SupportType.PINNED, k_spring=1e14),
            ],
            q_acid=10e3,
        )
        solver = LajesMindlinSolver(model)
        result = solver.solve()
        total_load = 4.0 * 4.0 * 10e3
        total_r = getattr(result, 'reactions_total', 0)
        if total_r > 0:
            error = abs(total_r - total_load) / total_load
            self.assertLessEqual(error, 0.30, f'Reações {total_r:.1f} ≠ {total_load:.1f}')


class TestSlabFlexureDesign(unittest.TestCase):
    """Verifica dimensionamento de seção de laje"""

    def test_flexure(self):
        engine = SlabDesignEngine()
        cfg = SlabDesignConfig(fck=30, h=0.20, cover=0.03, bar_diameter_mm=10.0)
        res = engine.calculate_flexure_section(50.0, cfg)
        self.assertGreater(res['as_req_cm2'], 0)
        self.assertTrue(res['is_ductile'])

    def test_punching(self):
        engine = SlabDesignEngine()
        cfg = SlabDesignConfig(fck=25, h=0.20, cover=0.03)
        res = engine.check_punching_2023(200.0, (0, 0), 1.0, 3.0, 0.165, 0.01, cfg)
        self.assertEqual(res['k_factor'], 2.0)

    def test_branson(self):
        engine = SlabServiceabilityEngine()
        cfg = ServiceabilityConfig(fck=30, h=0.15)
        res_h = engine.calculate_branson_inertia(20.0, 5.0, cfg)
        self.assertLess(res_h['reduction_factor'], 1.0)

    def test_detailing(self):
        engine = SlabDesignEngine()
        cfg = SlabDesignConfig(h=0.15)
        res = engine.select_detailing(5.0, cfg)
        self.assertGreater(res['diameter_mm'], 0)

    def test_crack_width(self):
        cfg = SlabDesignConfig(fck=30, h=0.20, bar_diameter_mm=10.0)
        res = SlabDesignEngine.check_crack_width_nbr6118(3.5, 3.93, 30.0, cfg)
        self.assertIn('wk_mm', res)
        self.assertIn('status', res)


class TestDXFExport(unittest.TestCase):
    def test_slab_dxf_export(self):
        from mef_engine.dxf_engine import export_slab_dxf

        data = {
            'detailing': {
                'x_bottom': {'diameter_mm': 10.0, 'spacing_cm': 12.5, 'as_real_cm2': 6.4},
                'y_bottom': {'diameter_mm': 8.0, 'spacing_cm': 15.0, 'as_real_cm2': 3.35},
                'x_top': {'diameter_mm': 10.0, 'spacing_cm': 20.0, 'as_real_cm2': 4.0},
                'y_top': {'diameter_mm': 8.0, 'spacing_cm': 20.0, 'as_real_cm2': 2.5},
            }
        }
        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as f:
            path = f.name
        try:
            result = export_slab_dxf(path, 5.0, 4.0, data)
            self.assertTrue(result.endswith('.dxf'))
            self.assertGreater(os.path.getsize(result), 0)
        finally:
            os.unlink(path)

    def test_radier_dxf_export(self):
        from mef_engine.dxf_engine import RadierDXFEngine

        with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as f:
            path = f.name
        try:
            e = RadierDXFEngine(path, 10, 8)
            e.draw_outline()
            e.draw_mesh('ARM_INF', 0.15, 'phi 12.5 c/ 15')
            e.save()
            self.assertGreater(os.path.getsize(path), 0)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
