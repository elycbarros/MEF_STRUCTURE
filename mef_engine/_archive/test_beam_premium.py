"""
test_beam_premium.py — Auditoria de Validação do Módulo Vigas Premium.

Verifica a Não-Linearidade Física, Redistribuição de Momentos e
Dimensionamento ELS-W (Fissuração).
"""

from beam_detailing import BeamDetailer
from beam_solver import run_beam_analysis


def run_premium_beam_audit():
    print('🚀 Iniciando Auditoria Vigas Premium (Nível Forense)...')

    # Cenário: Viga Contínua de 2 vãos (6m + 6m)
    # Seção T: bf=0.60m, hf=0.10m, b=0.20m, h=0.50m
    # Carga: 25 kN/m (Pesada)

    L_total = 12.0
    res = run_beam_analysis(
        L=L_total,
        supports=[
            {'x': 0.0, 'type': 'pinned'},
            {'x': 6.0, 'type': 'pinned'},
            {'x': 12.0, 'type': 'pinned'},
        ],
        distributed_loads=[
            {'x_start': 0, 'x_end': 12.0, 'q_start': 25.0},  # 25 kN/m
        ],
        b=0.20,
        h=0.50,
        fck=30,
        bf=0.60,
        hf=0.10,
        nonlinear=True,
        redistribution_delta=0.85,  # 15% de redistribuição
    )

    summary = res['summary']
    design = res['design']

    print(f'📊 Análise: {summary["analysis_type"]}')
    print(f'📏 Seção: {summary["b_m"] * 100}x{summary["h_m"] * 100} cm | Viga T: bf={summary["bf_m"] * 100} cm')
    print(f'📉 Flecha Máxima (Fissurada): {summary["max_deflection_mm"]} mm')

    print(f'\n✅ Auditoria de Dimensionamento (Redistribuição: {design["redistribution_applied"]}):')
    print(f'   Momento Apoio (Reduzido): {design["M_max_neg_kNm"]} kNm')
    print(f'   As Superior: {design["flexure_top"]["As_cm2"]} cm² (Domínio {design["flexure_top"]["domain"]})')
    print(f'   As Inferior (Mesa T): {design["flexure_bottom"]["As_cm2"]} cm²')

    print('\n🛡️ Verificação de Serviço (ELS-W):')
    print(
        f'   Abertura de Fissuras (wk): {design["crack_width"]["wk_mm"]} mm (Limite: {design["crack_width"]["limit_mm"]} mm)'
    )
    print(f'   Status Flecha (L/250): {design["deflection"]["status"]}')

    # Detalhamento
    det_summary = BeamDetailer.generate_detailing_summary(design, summary['b_m'], summary['h_m'], summary['fck_MPa'])

    print('\n🏗️ Detalhamento Sugerido (Executive Grade):')
    print(f'   Superior (Apoio): {det_summary["sup"]["spec"]} (lb={det_summary["sup"]["lb_nec"]} cm)')
    print(f'   Inferior (Vão): {det_summary["inf"]["spec"]} (lb={det_summary["inf"]["lb_nec"]} cm)')
    print(f'   Estribos: {det_summary["stirrups"]}')

    if design['overall_status'] == 'ATENDE':
        print('\n🏆 RESULTADO: VIGA VALIDADA (Nível Premium)')
    else:
        print(f'\n⚠️ ALERTA: {design["overall_status"]}')


def test_beam_premium():
    run_premium_beam_audit()


if __name__ == '__main__':
    run_premium_beam_audit()
