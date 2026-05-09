import requests
import json

url = "http://localhost:8000/api/ufo/calculate/beam"
payload = {
    "L": 6.0,
    "b": 0.20,
    "h": 0.50,
    "fck": 30,
    "caa": 2,
    "supports": [
        {"x": 0.0, "type": "pinned"},
        {"x": 6.0, "type": "pinned"}
    ],
    "distributed_loads": [
        {"x_start": 0.0, "x_end": 6.0, "q_start": 20.0, "q_end": 20.0}
    ],
    "n_elements": 40,
    "include_self_weight": True
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
