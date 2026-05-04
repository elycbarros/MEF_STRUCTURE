"""
test_building_stability.py — Auditoria Forense de Estabilidade Global 3D.

Integra o Frame3DEngine com o WindEngine (NBR 6123) para análise P-Delta
completa de edifícios de múltiplos pavimentos.
"""
import numpy as np
from frame_engine import FrameNode, FrameSection, FrameMember, FrameLoad, Frame3DEngine
from wind_engine import WindEngine, WindConfig

def build_multi_story_frame(n_floors: int, floor_height: float, section: FrameSection) -> tuple:
    """Constrói o modelo de pórtico para N pavimentos (pórtico plano 2D em 3D)."""
    nodes = []
    members = []

    for floor in range(n_floors + 1):
        z = floor * floor_height
        nodes.append(FrameNode(id=floor*2,     x=0.0, y=0.0, z=z))
        nodes.append(FrameNode(id=floor*2 + 1, x=5.0, y=0.0, z=z))

    member_id = 0
    for floor in range(n_floors):
        members.append(FrameMember(id=member_id, node_i=floor*2,     node_j=(floor+1)*2,     section=section))
        member_id += 1
        members.append(FrameMember(id=member_id, node_i=floor*2 + 1, node_j=(floor+1)*2 + 1, section=section))
        member_id += 1
        beam_section = FrameSection(b=0.20, h=0.50, E=section.E)
        members.append(FrameMember(id=member_id, node_i=(floor+1)*2, node_j=(floor+1)*2 + 1, section=beam_section))
        member_id += 1

    return nodes, members


def run_3d_stability_audit():
    print("🏗️  Auditoria Forense de Estabilidade Global — NBR 6118 + NBR 6123")
    print("=" * 65)

    n_floors    = 10
    floor_h     = 3.0
    total_h     = n_floors * floor_h
    P_por_pav   = 500_000  # N

    E_reduz = 0.8 * 2.5e10  # NBR 6118 §15.7.3: 0.8·EI para pilares
    sec_col = FrameSection(b=0.40, h=0.40, E=E_reduz)

    nodes, members = build_multi_story_frame(n_floors, floor_h, sec_col)
    engine = Frame3DEngine(nodes, members)

    gravity_loads = []
    for floor in range(1, n_floors + 1):
        P_acum = P_por_pav * floor
        gravity_loads.append(FrameLoad(node_id=floor*2,     Fz=-P_acum / 2))
        gravity_loads.append(FrameLoad(node_id=floor*2 + 1, Fz=-P_acum / 2))

    cfg  = WindConfig(v0=45.0, categoria=3, classe='B')
    weng = WindEngine(cfg)
    Cp, width = 0.8, 5.0

    wind_loads = []
    for floor in range(1, n_floors + 1):
        z      = floor * floor_h
        q_v    = WindEngine.calculate_dynamic_pressure(z, cfg)
        F_wind = q_v * Cp * width * floor_h
        # Vento no nó de barlavento de cada pavimento (nó esquerdo)
        wind_loads.append(FrameLoad(node_id=floor*2, Fx=F_wind))

    all_loads = gravity_loads + wind_loads
    supports  = {0: [0,1,2,3,4,5], 1: [0,1,2,3,4,5]}

    res1 = engine.solve(all_loads, supports)
    delta_top_1 = abs(res1['displacements'][n_floors*2][0])

    res2 = engine.solve_p_delta(all_loads, supports, max_iter=15)
    delta_top_2 = abs(res2['displacements'][n_floors*2][0])

    p_delta_factor = delta_top_2 / delta_top_1 if delta_top_1 > 1e-9 else 1.0
    delta_lim      = total_h / 400.0
    drift_ratio    = delta_top_2 / total_h
    q_topo         = WindEngine.calculate_dynamic_pressure(total_h, cfg)
    F_topo         = q_topo * Cp * width * floor_h

    print(f"\n📐 Modelo: {n_floors} Pavimentos | H={total_h}m | 2 Colunas {int(sec_col.b*100)}×{int(sec_col.h*100)}cm")
    print(f"💨 Vento: V₀={cfg.v0} m/s | Cat.{cfg.categoria}-Classe {cfg.classe} | F_topo≈{F_topo/1000:.1f} kN")
    print(f"⚖️  Carga Axial por Coluna (base): {P_por_pav*n_floors/2/1000:.0f} kN")
    print()
    print(f"{'Parâmetro':<38} {'Valor':>12}")
    print("-" * 52)
    print(f"{'Deslocamento 1ª Ordem (mm)':<38} {delta_top_1*1000:>12.2f}")
    print(f"{'Deslocamento P-Delta / 2ª Ordem (mm)':<38} {delta_top_2*1000:>12.2f}")
    print(f"{'Fator γz equivalente':<38} {p_delta_factor:>12.3f}")
    print(f"{'Limite H/400 (mm)':<38} {delta_lim*1000:>12.1f}")
    print(f"{'Drift Total (Δ/H)':<38} {drift_ratio:>12.5f}")
    print()

    if p_delta_factor <= 1.10:
        cls = "✅ NÃO-SENSÍVEL (γz ≤ 1.10)"
    elif p_delta_factor <= 1.30:
        cls = "⚠️  SENSÍVEL — 2ª Ordem obrigatória (1.10 < γz ≤ 1.30)"
    else:
        cls = "🚨 INSTÁVEL — γz > 1.30 | Rever rigidez lateral!"

    deslocamento_ok = delta_top_2 <= delta_lim
    print(f"Classificação NBR 6118 §15.5.2:  {cls}")
    print(f"Deslocamento H/400:               {'✅ OK' if deslocamento_ok else '❌ EXCEDE'}")

    if p_delta_factor <= 1.30 and deslocamento_ok:
        print("\n🏆 AUDITORIA APROVADA — Estrutura globalmente estável.")
    else:
        print("\n⚠️  REVISÃO NECESSÁRIA — Aumentar rigidez (núcleos, paredes de corte).")


if __name__ == "__main__":
    run_3d_stability_audit()
