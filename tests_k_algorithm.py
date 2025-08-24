import json
import time
import sys
from http.client import HTTPConnection
from functools import lru_cache

HOST = "localhost"
PORT = 8000
PATH = "/api/hanoi"
N_KEY = "size"         

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

# ---------------------------
# Oraculo independiente (Frame–Stewart) para validar # de movimientos
# ---------------------------
@lru_cache(maxsize=None)
def min_moves(n: int, k: int) -> int:
    if n <= 0:
        return 0
    if n == 1:
        return 1
    if k <= 3:
        return (1 << n) - 1  # 2^n - 1

    best = float("inf")
    for t in range(1, n):
        cand = 2 * min_moves(t, k) + min_moves(n - t, k - 1)
        if cand < best:
            best = cand
    return int(best)

def is_steps_well_formed(steps, allowed_labels=None):
    """
    Verifica que steps sea lista de pasos en formato:
      [disk:int, from:str, to:str]
    Y (opcional) que from/to pertenezcan a allowed_labels.
    """
    if not isinstance(steps, list):
        return False
    for m in steps:
        if not (isinstance(m, list) and len(m) == 3):
            return False
        disk, f, t = m
        if not (isinstance(disk, int) and isinstance(f, str) and isinstance(t, str)):
            return False
        if allowed_labels is not None and (f not in allowed_labels or t not in allowed_labels):
            return False
    return True

def test_k3_equiv():
    """Para k=3 debe coincidir con 2^n - 1 y estar bien formado."""
    for n in range(1, 8):
        status, data = post_json({N_KEY: n, "k": 3})
        assert status == 200, f"HTTP {status} en k=3, n={n}"
        assert isinstance(data, list), "Respuesta no es lista"
        assert len(data) == (1 << n) - 1, f"Len incorrecto para n={n}, k=3"
        assert is_steps_well_formed(data), "Pasos mal formados en k=3"

def test_k4_small_ns():
    """Valida para k=4 algunos n pequeños contra el oráculo Frame–Stewart."""
    for n in range(1, 9):
        status, data = post_json({N_KEY: n, "k": 4})
        assert status == 200, f"HTTP {status} en k=4, n={n}"
        expected = min_moves(n, 4)
        assert isinstance(data, list), "Respuesta no es lista"
        assert len(data) == expected, f"(k=4, n={n}) esperado {expected}, obtuve {len(data)}"
        assert is_steps_well_formed(data), "Pasos mal formados en k=4"

def test_custom_pegs_and_from_to():
    """Prueba pegs personalizados y from/to no triviales."""
    pegs = ["P1", "P2", "P3", "P4", "P5"]
    status, data = post_json({N_KEY: 5, "pegs": pegs, "from": "P2", "to": "P5"})
    assert status == 200, f"HTTP {status}"
    assert isinstance(data, list) and len(data) == min_moves(5, len(pegs))
    assert is_steps_well_formed(data, allowed_labels=set(pegs))

def test_zero_and_invalids():
    """n=0 -> []; content-type inválido -> []; parámetros inválidos -> []"""
    # n == 0
    status, data = post_json({N_KEY: 0, "k": 4})
    assert status == 200 and data == [], "n=0 debe devolver []"

    # Content-Type inválido
    status, data = post_json({N_KEY: 4, "k": 4}, content_type="text/plain")
    assert status == 200 and data == [], "content-type inválido debe devolver []"

    # k inválido
    status, data = post_json({N_KEY: 4, "k": 2})
    assert status == 200 and data == [], "k<3 debe devolver []"

    # pegs duplicados
    status, data = post_json({N_KEY: 3, "pegs": ["A", "A", "B"]})
    assert status == 200 and data == [], "pegs duplicados deben devolver []"

    # 'to' igual a 'from'
    status, data = post_json({N_KEY: 3, "pegs": ["X", "Y", "Z"], "from": "X", "to": "X"})
    assert status == 200 and isinstance(data, list), "Debe responder 200 con lista (posible [] o solución válida)"

def test_labels_default_generation():
    """Si solo se pasa k debe generar etiquetas por defecto y responder"""
    status, data = post_json({N_KEY: 4, "k": 5})
    assert status == 200 and isinstance(data, list)
    assert len(data) == min_moves(4, 5), "Conteo de movimientos no coincide para k=5"
    # También valida estructura [disk, from, to]
    assert is_steps_well_formed(data), "Formato de pasos inválido con k=5"

def main():
    time.sleep(0.3)
    print(">> Ejecutando pruebas /hanoi_k (formato [disk, from, to]) ...")
    test_k3_equiv()
    print("OK: k=3 coincide con 2^n-1 y formato correcto")
    test_k4_small_ns()
    print("OK: k=4 coincide con oráculo Frame–Stewart (n=1..8)")
    test_custom_pegs_and_from_to()
    print("OK: pegs personalizados y from/to válidos")
    test_zero_and_invalids()
    print("OK: casos n=0, content-type inválido y parámetros inválidos")
    test_labels_default_generation()
    print("OK: generación de etiquetas por defecto y formato correcto")

    print("\nTodas las pruebas de /hanoi_k pasaron ✔")

if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print("Fallo de prueba:", e)
        sys.exit(1)
