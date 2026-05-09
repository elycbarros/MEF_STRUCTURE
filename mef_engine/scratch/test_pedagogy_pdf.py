import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao path para importar os módulos locais
sys.path.append(str(Path(__file__).parent.parent))

from reporting.pedagogy.beam import build_beam_blackboard
from academic_pdf import generate_academic_blackboard_pdf

def test_pdf_generation():
    print("Iniciando teste de geração de PDF blindado...")
    
    # 1. Simular resultado de cálculo de viga
    mock_result = {
        "fck": 30,
        "fy": 500,
        "b": 0.20,
        "h": 0.50,
        "L": 5.0,
        "M_max_kNm": 120.0,
        "As_calc": 6.5,
        "w_max_mm": 12.0,
        "w_limit_mm": 20.0,
        "summary": {"Status": "Aprovado", "Material": "Concreto C30"}
    }
    
    # 2. Gerar Blackboard usando o novo motor modular
    blackboard = build_beam_blackboard(mock_result, mock_result)
    
    # 3. Definir caminho de saída
    output_pdf = Path(__file__).parent / "test_memorial_blindado.pdf"
    
    # 4. Gerar PDF
    try:
        path = generate_academic_blackboard_pdf(
            output_path=output_pdf,
            blackboard=blackboard,
            project_meta={"disciplina": "Estruturas de Concreto I", "professor": "Mestre Structural"}
        )
        print(f"Sucesso! PDF gerado em: {path}")
    except Exception as e:
        print(f"Erro na geração do PDF: {e}")

if __name__ == "__main__":
    test_pdf_generation()
