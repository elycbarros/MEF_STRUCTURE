"""
test_lajes_lab.py - Teste de validação para o Módulo de Lajes Elevadas.
"""

import json
from pathlib import Path

from radier_lab_v24 import LabConfig, run_design_checks, run_deterministic_fem
from radier_utils import ensure_directory


def test_lajes_module():
    out_dir = 'output_lajes_test'
    ensure_directory(out_dir)

    # Configuração para Laje Elevada (Lajes Lab)
    config = LabConfig(
        module_name='lajes',
        base_name='laje_elevada_test',
        output_dir=out_dir,
        Lx=8.0,
        Ly=8.0,
        nx=21,
        ny=21,
        h=0.20,  # 20cm
        fck=30.0,
        q=2000.0,  # Carga acidental + revestimento (2 kN/m2)
        concrete_nonlinear=True,  # Ativa NLF para flechas reais
    )

    print('🚀 Iniciando Simulação Lajes Lab (Laje Elevada)...')

    # 1. Executa FEM (com NLF)
    summary_path = run_deterministic_fem(config)

    # 2. Executa Pipeline de Design (Punção, Flexão, Flechas)
    results = run_design_checks(config)

    print('\n✅ Simulação Concluída!')

    # Verificação básica
    det_summary_path = Path(out_dir) / f'{config.base_name}_deterministic_summary.json'
    with open(det_summary_path, 'r') as f:
        det_summary = json.load(f)
    w_max = det_summary.get('w_max_mm', 0)
    print(f'📐 Flecha Máxima (com NLF): {w_max:.2f} mm')

    # Se a flecha for zero ou muito próxima de zero com kv=0 e sem apoios, algo está errado.
    # Mas como o solver converte pilares em apoios, deve haver deformação entre pilares.

    if w_max > 0:
        print('✅ Deformação detectada entre apoios discretos.')
    else:
        print('❌ Erro: Laje sem deformação (verificar apoios).')


if __name__ == '__main__':
    test_lajes_module()
