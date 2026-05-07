import requests
import sys

def test_beam_pdf():
    url = "http://127.0.0.1:8000/export/academic/beam"
    payload = {
        "L": 6.0,
        "b": 0.2,
        "h": 0.5,
        "fck": 30,
        "caa": 2,
        "supports": [{"x": 0.0, "type": "pinned"}, {"x": 6.0, "type": "pinned"}],
        "distributed_loads": [{"x_start": 0, "x_end": 6, "q_start": 20000}],
    }
    try:
        print(f"Sending request to {url}...")
        res = requests.post(url, json=payload)
        print(f"Status Code: {res.status_code}")
        if res.status_code != 200:
            print("Error Response:")
            print(res.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_beam_pdf()
