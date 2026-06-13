import json

import requests

url = 'http://localhost:8000/api/mestre/calculate/special-elements'
payload = {'type': 'beam', 'params': {'L': 5.0, 'b': 0.20, 'h': 0.40, 'q': 10.0, 'fck': 30.0}}

try:
    response = requests.post(url, json=payload)
    print(f'Status: {response.status_code}')
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f'Error: {e}')
