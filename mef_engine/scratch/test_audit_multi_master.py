
import sys
import os
sys.path.append(os.path.abspath('.'))

from master_pedagogy import build_composite_pedagogy, build_forensic_audit
import json

# 1. Simular resultados MEF e Analíticos
mef_res = {
    "summary": {
        "total_load_kN": 135.0,
        "total_reaction_kN": 134.8, # Erro de 0.15%
        "max_moment_kNm": 101.25,
        "max_shear_kN": 67.5
    }
}

analytical_res = {
    "max_moment_kNm": 100.0 # Divergência de 1.25%
}

print("--- TESTE AUDITORIA FORENSE ---")
audit_blackboard = build_forensic_audit("viga", mef_res, analytical_res)
print(f"Status Auditoria: {audit_blackboard['metadata']['audit_status']}")
for step in audit_blackboard['steps']:
    print(f"[{step['id']}] {step['title']}: {step['result']}")

print("\n--- TESTE MULTI-MESTRE (COMPOSITE) ---")
configs = [
    {"type": "beam", "result": mef_res, "payload": {"L": 6.0}},
    {"type": "audit", "result": mef_res, "payload": {"element_type": "beam", "analytical": analytical_res}}
]
composite = build_composite_pedagogy(configs)
print(f"Título: {composite['metadata']['title']}")
print(f"Total de Passos: {len(composite['steps'])}")
print(f"Exemplo de ID Composto: {composite['steps'][0]['id']}")
