import os
import sys
import unittest
from fastapi.testclient import TestClient

# Adicionar CWD ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api import app

class TestExamAuditor(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_q47_fcc_2018(self):
        print("\n--- Testando Questão 47 - FCC 2018 ---")
        payload = {
            "type": "exam_auditor",
            "params": {
                "question_id": "q47_fcc_2018"
            }
        }
        response = self.client.post("/api/mestre/calculate/special-elements", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        
        res = data["result"]
        self.assertEqual(res["question_id"], "q47_fcc_2018")
        self.assertEqual(res["correct_reactions"]["Ra"], -10.0)
        self.assertEqual(res["correct_reactions"]["Rb"], 40.0)
        self.assertEqual(res["status"], "INVÁLIDA (Erro de Equilíbrio Físico)")
        
        steps = data["pedagogical_steps"]
        self.assertEqual(steps["metadata"]["title"], "Laudo Pericial: Auditoria de Questões de Exames")
        self.assertEqual(len(steps["steps"]), 4) # Base normativa + 2 steps + validation
        
        print("Reações física reais calculadas: Ra = -10 kN, Rb = 40 kN.")
        print("Duelo comparativo gerado com sucesso!")
        
        # Verificar existência do PDF
        pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/reports/memorial_questao_47.pdf")
        self.assertTrue(os.path.exists(pdf_path), f"PDF do memorial não encontrado em: {pdf_path}")
        print("PDF pericial verificado no disco: memorial_questao_47.pdf")

    def test_q31_vunesp_2021(self):
        print("\n--- Testando Questão 31 - VUNESP 2021 ---")
        payload = {
            "type": "exam_auditor",
            "params": {
                "question_id": "q31_vunesp_2021"
            }
        }
        response = self.client.post("/api/mestre/calculate/special-elements", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        
        res = data["result"]
        self.assertEqual(res["question_id"], "q31_vunesp_2021")
        self.assertEqual(res["correct_reactions"]["Ra"], -40.0)
        self.assertEqual(res["correct_reactions"]["Rb"], 60.0)
        
        steps = data["pedagogical_steps"]
        self.assertEqual(steps["metadata"]["title"], "Laudo Pericial: Auditoria de Questões de Exames")
        
        # Verificar existência do PDF
        pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/reports/memorial_questao_31.pdf")
        self.assertTrue(os.path.exists(pdf_path), f"PDF do memorial não encontrado em: {pdf_path}")
        print("PDF pericial verificado no disco: memorial_questao_31.pdf")

if __name__ == "__main__":
    unittest.main()
