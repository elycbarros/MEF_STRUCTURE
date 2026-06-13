from engines.column_engine import ColumnEngine
from reporting.pedagogy.special import build_pillar_wall_blackboard


def test_solve_pillar_wall_logic():
    # Test column with small dimension (b=15cm, h=80cm) -> gamma_n = 1.95 - 0.05*15 = 1.20
    # ratio = 80 / 15 = 5.33 >= 5.0 (so is_pillar_wall should be True)
    res = ColumnEngine.solve_pillar_wall(
        nd_kN=1000.0, mdx_kNm=20.0, mdy_kNm=10.0, h=0.80, b=0.15, l_e=3.0, fck=30.0, caa=2
    )

    assert res['is_pillar_wall'] is True
    assert res['gamma_n'] == 1.20
    assert res['nd_adjusted_kN'] == 1200.0
    print('DEBUG: status =', res['status'])
    print('DEBUG: As_final =', res['As_final_cm2'])
    assert res['status'] in ('OK', 'TAXA_ALTA_CONGESTIONADA', 'ALTA_ESBELTEZ', 'FORA_DIAGRAMA_INTERACAO')
    assert 'detailing' in res
    assert res['detailing']['longitudinal']['count'] > 0

    # Test blackboard build
    blackboard = build_pillar_wall_blackboard(res)
    assert 'steps' in blackboard
    assert len(blackboard['steps']) >= 4


def test_solve_pillar_wall_not_wall():
    # b=40cm, h=40cm -> ratio = 1.0 < 5.0 -> is_pillar_wall should be False
    res = ColumnEngine.solve_pillar_wall(
        nd_kN=500.0, mdx_kNm=0.0, mdy_kNm=0.0, h=0.40, b=0.40, l_e=3.0, fck=30.0, caa=2
    )
    assert res['is_pillar_wall'] is False
    print('DEBUG 2: status =', res['status'])
    assert res['status'] in ('SECAO_NAO_PAREDE', 'FORA_DIAGRAMA_INTERACAO')


if __name__ == '__main__':
    test_solve_pillar_wall_logic()
    test_solve_pillar_wall_not_wall()
    print('All backend tests for Pillar-Wall passed!')
