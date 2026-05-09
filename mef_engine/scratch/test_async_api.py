import sys
import os
import time
import requests
import json

# Start the server in background if not running (assuming it's running on 8000)
URL = "http://localhost:8000"

def test_async_frame():
    # Modelo simples para teste
    payload = {
        "nodes": [
            {"id": 1, "x": 0.0, "y": 0.0, "z": 0.0},
            {"id": 2, "x": 0.0, "y": 0.0, "z": 3.0}
        ],
        "members": [
            {
                "id": 1, "node_i": 1, "node_j": 2,
                "section": {"b": 0.2, "h": 0.5, "E": 2.5e10, "G": 1.0e10},
                "type": "column"
            }
        ],
        "loads": [
            {"node_id": 2, "Fx": 10000.0}
        ],
        "supports": {"1": [0,1,2,3,4,5]},
        "use_p_delta": True,
        "nbr_stiffness_reduction": True
    }

    print("🚀 Enviando análise assíncrona...")
    r = requests.post(f"{URL}/api/ufo/calculate/frame/async", json=payload)
    if r.status_code != 200:
        print(f"❌ Erro ao enviar: {r.text}")
        return

    job_id = r.json()["job_id"]
    print(f"✅ Job ID: {job_id}")

    # Polling
    for _ in range(10):
        r = requests.get(f"{URL}/api/ufo/jobs/{job_id}")
        job = r.json()
        status = job["status"]
        progress = job["progress"]
        print(f"⏳ Status: {status} ({progress}%)")
        
        if status == "completed":
            print("✨ Job concluído com sucesso!")
            # print(json.dumps(job["result"], indent=2))
            return
        elif status == "failed":
            print(f"❌ Job falhou: {job['error']}")
            return
        
        time.sleep(1)

if __name__ == "__main__":
    # Nota: Este teste assume que o servidor está rodando.
    # Em um ambiente de CI, iniciaríamos o uvicorn aqui.
    try:
        test_async_frame()
    except Exception as e:
        print(f"⚠️ Servidor não disponível ou erro: {e}")
