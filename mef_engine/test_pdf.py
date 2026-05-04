from academic_pdf import generate_academic_blackboard_pdf
import os

blackboard = {
    "title": "Teste de Robustez LaTeX",
    "steps": [
        {
            "title": "Verificacao de Flexao",
            "formula_latex": r"A_s = \frac{M_{sd}}{f_{yd} \cdot d \cdot (1 - 0.4 \cdot x/d)}",
            "substitution_latex": r"A_s = \frac{150.0}{43.48 \cdot 0.45 \cdot (1 - 0.4 \cdot 0.259)}",
            "result_latex": r"A_s = 8.56 \, cm^2",
            "status": "OK",
            "opinion": "Atende aos criterios."
        }
    ]
}

output_path = "output_api/test_latex_robustness.pdf"
generate_academic_blackboard_pdf(output_path, blackboard)
print(f"PDF gerado em: {os.path.abspath(output_path)}")
