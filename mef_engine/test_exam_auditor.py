import unittest
import tempfile
from pathlib import Path

from exam_auditor import build_professional_pdf_payload
from professional_pdf import generate_professional_memorial
from special_elements import SpecialElementsSolver
from reporting.pedagogy.special import build_exam_auditor_blackboard


class TestExamAuditor(unittest.TestCase):
    def test_q47_fcc_2018(self):
        res = SpecialElementsSolver.solve_exam_auditor("q47_fcc_2018")

        self.assertEqual(res["question_id"], "q47_fcc_2018")
        self.assertEqual(res["status"], "INVÁLIDA (Erro de Equilíbrio Físico)")
        self.assertAlmostEqual(res["correct_reactions"]["Ra"], -10.0, places=6)
        self.assertAlmostEqual(res["correct_reactions"]["Rb"], 40.0, places=6)
        self.assertEqual(res["exam_reactions"], {"Ra": 10.0, "Rb": 20.0})
        self.assertEqual(res["model"]["length_m"], 8.0)
        self.assertAlmostEqual(res["solver_result"]["summary"]["max_moment_kNm"], 60.0, places=2)

        blackboard = build_exam_auditor_blackboard(res)
        steps = {step["id"]: step for step in blackboard["steps"]}
        self.assertIn("8,0 m", steps["q47-moments"]["explanation"])
        self.assertIn("R_A = -10,0", steps["q47-moments"]["result"])
        self.assertIn("R_B = 40,0", steps["q47-vertical"]["result"])
        self.assertIn("Rb = 20,0 kN", steps["q47-audit"]["explanation"])

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "q47.pdf"
            pdf_results, pdf_meta = build_professional_pdf_payload(res)
            generate_professional_memorial(str(output), pdf_results, pdf_meta)
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 1000)

    def test_q31_vunesp_2021(self):
        res = SpecialElementsSolver.solve_exam_auditor("q31_vunesp_2021")

        self.assertEqual(res["question_id"], "q31_vunesp_2021")
        self.assertEqual(res["status"], "INVÁLIDA (Erro de Cálculo da Formulação)")
        self.assertAlmostEqual(res["correct_reactions"]["Ra"], -40.0, places=6)
        self.assertAlmostEqual(res["correct_reactions"]["Rb"], 60.0, places=6)
        self.assertAlmostEqual(res["correct_reactions"]["Rax"], -20.0, places=6)
        self.assertAlmostEqual(res["solver_result"]["member_efforts"][2]["i"]["N"], -20.0, places=2)
        self.assertAlmostEqual(res["solver_result"]["member_efforts"][7]["i"]["N"], 28.284271, places=5)

        blackboard = build_exam_auditor_blackboard(res)
        steps = {step["id"]: step for step in blackboard["steps"]}
        self.assertIn("R_{Ax} = -20,0", steps["q31-reactions"]["result"])
        self.assertIn("N_{sup} = -20,00", steps["q31-axial"]["substitution"])
        self.assertIn("N_{diag} = 28,28", steps["q31-axial"]["substitution"])
        self.assertIn("Rax = 20,0 kN", steps["q31-audit"]["explanation"])

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "q31.pdf"
            pdf_results, pdf_meta = build_professional_pdf_payload(res)
            generate_professional_memorial(str(output), pdf_results, pdf_meta)
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 1000)


if __name__ == "__main__":
    unittest.main()
