"""
MEF STRUCTURAL - Matriz de Validação e Benchmarks (Fase 1)
Centraliza os casos de teste analíticos e numéricos para garantir a confiabilidade dos motores.
"""

VALIDATION_BENCHMARKS = {
    "radier": [
        {
            "id": "RAD-001",
            "name": "Placa Rígida sobre Solo Elástico (Carga Uniforme)",
            "description": "Radier retangular com carga uniforme. Pressão deve ser P/A.",
            "inputs": {
                "Lx": 10.0, "Ly": 10.0, "h": 0.50, "fck": 30, "kv": 10000, "q": 10.0
            },
            "expected": {
                "pressao_media_kPa": 10.0,
                "recalque_medio_mm": 1.0, # q/kv = 10/10000 = 0.001m = 1mm
                "tolerance_pct": 1.0
            }
        },
        {
            "id": "RAD-002",
            "name": "Punção em Laje Espessa (Caso Central)",
            "description": "Verificação de punção contra cálculo manual NBR 6118.",
            "inputs": {
                "h": 0.60, "d": 0.55, "fck": 30, "pilar_load_kN": 1000, "pilar_dim": 0.40
            },
            "expected": {
                "tau_rd1_min": 0.50, # MPa (valor de ordem de grandeza)
                "atende": True
            }
        }
    ],
    "beam": [
        {
            "id": "BEAM-001",
            "name": "Viga Bi-apoiada Carga Uniforme",
            "description": "Viga isostática. M = qL^2/8.",
            "inputs": {
                "L": 5.0, "q": 20.0, "bw": 0.20, "h": 0.50
            },
            "expected": {
                "moment_max_kNm": 62.5,
                "shear_max_kN": 50.0,
                "tolerance_pct": 0.1
            }
        }
    ],
    "frame": [
        {
            "id": "FRAME-001",
            "name": "Pórtico Simples P-Delta (Benchmark de Estabilidade)",
            "description": "Pórtico plano com carga vertical e horizontal para validar gamma-z.",
            "inputs": {
                "height": 3.0, "width": 5.0, "vertical_load": 1000, "horizontal_load": 50
            },
            "expected": {
                "gamma_z_approx": 1.05,
                "is_stable": True
            }
        }
    ]
}

def get_benchmark(module: str, benchmark_id: str):
    module_benchs = VALIDATION_BENCHMARKS.get(module, [])
    for b in module_benchs:
        if b["id"] == benchmark_id:
            return b
    return None
