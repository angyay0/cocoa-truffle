import json
import sys
import time
from http.client import HTTPConnection

HOST = "localhost"
PORT = 8000
PATH = "/api/hanoi"

def post_json(payload, content_type="application/json"):
    conn = HTTPConnection(HOST, PORT, timeout=5)
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": content_type}
    conn.request("POST", PATH, body=body, headers=headers)
    resp = conn.getresponse()
    data = resp.read()
    conn.close()
    try:
        parsed = json.loads(data.decode("utf-8"))
    except Exception:
        parsed = data.decode("utf-8", errors="ignore")
    return resp.status, parsed

def main():
    time.sleep(0.3)

    # 1) Happy path: n=3
    status, data = post_json({"size": 3, "k": 3})
    assert status == 200, f"Status inesperado: {status}"
    assert isinstance(data, list) and len(data) == 7, f"Pasos esperados 7, obtuve {len(data)}"
    print("OK: n=3 produce 7 pasos")

    # 2) Content-Type incorrecto -> []
    status, data = post_json({"size": 3, "k": 3}, content_type="text/plain")
    assert status == 200 and data == [], "Debe devolver [] en content-type inválido"
    print("OK: content-type inválido devuelve []")

    # 3) JSON inválido -> []
    conn = HTTPConnection(HOST, PORT, timeout=5)
    conn.request("POST", PATH, body=b"not-json", headers={"Content-Type": "application/json"})
    resp = conn.getresponse()
    body = resp.read().decode("utf-8")
    conn.close()
    parsed = json.loads(body)
    assert resp.status == 200 and parsed == [], "Debe devolver [] en JSON inválido"
    print("OK: JSON inválido devuelve []")

    # 4) Limite n demasiado grande -> []
    status, data = post_json({"size": 10**9, "k": 3})
    assert status == 200 and data == [], "Debe devolver [] si n excede límites"
    print("OK: límite n grande devuelve []")

    # 5) Parametros personalizados
    status, data = post_json({"size": 2, "from": "X", "to": "Z", "pegs": ["X", "Y", "Z"]})
    assert status == 200 and isinstance(data, list) and len(data) == 3
    pairs = set(tuple(m) for m in data)
    assert all(isinstance(m, list) and len(m) == 2 for m in data)
    print("OK: parámetros personalizados funcionan")

    print("\nTodas las pruebas funcionales pasaron ✔")

if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("Fallo de prueba:", e)
        sys.exit(1)
