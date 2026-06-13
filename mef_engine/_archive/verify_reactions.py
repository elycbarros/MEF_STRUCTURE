from beam_solver import run_beam_analysis

# Teste para verificar a soma das reações
L = 6.0
supports = [{'x': 0.0, 'type': 'pinned'}, {'x': 6.0, 'type': 'pinned'}]
distributed_loads = [{'x_start': 0.0, 'x_end': 6.0, 'q_start': 20.0, 'q_end': 20.0}]  # 20 kN/m

result = run_beam_analysis(
    L=L,
    supports=supports,
    distributed_loads=distributed_loads,
    include_self_weight=True,  # b=0.2, h=0.5 -> pp = 0.1 * 25 = 2.5 kN/m
    b=0.2,
    h=0.5,
)

q_total = 20.0 + 2.5
expected_total = q_total * L  # 22.5 * 6 = 135 kN

reactions = result['reactions']
sum_r = sum(r['R'] for r in reactions.values())

print(f'Carga total aplicada: {expected_total} kN')
print(f'Soma das reações: {sum_r} kN')
print(f'Reações detalhadas: {reactions}')
