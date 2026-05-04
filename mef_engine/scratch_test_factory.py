
from memorial_factory import build_unified_memorial

def test_factory():
    m = build_unified_memorial(
        module_title="Teste de Memorial",
        engine_name="TestEngine",
        engine_version="1.0",
        hypotheses=["Hip 1", "Hip 2"],
        materials={"Concreto": "C30", "Aco": "CA-50"},
        loads={"Carga": "100 kN"},
        combinations=["ELU", "ELS"],
        model_details={"Malha": "10x10"},
        results={"Momento": "50 kNm"},
        verifications=[{"label": "Teste", "pass": True, "value": "10", "limit": "20"}],
        governing={"Pilar": "P1"},
        alerts=["Alerta 1"],
        limitations=["Lim 1"]
    )
    print(m)

if __name__ == "__main__":
    test_factory()
