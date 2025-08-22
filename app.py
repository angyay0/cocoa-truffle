# app.py
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Límite seguro por defecto (ajustable por variable de entorno)
MAX_N = int(os.getenv("MAX_N", "14"))  # 2^14-1 = 16383 pasos (JSON razonable)

def hanoi_steps_iter(n: int, src: str, dst: str, aux: str):
    """Genera la secuencia de pasos como tuplas (from, to) de forma iterativa (sin recursión)."""
    # Pila: (n, src, dst, aux, state)
    # state 0 => expandir, state 1 => emitir movimiento, state 2 => expandir segunda mitad
    stack = [(n, src, dst, aux, 0)]
    steps = []
    while stack:
        cur_n, s, d, a, state = stack.pop()
        if cur_n <= 0:
            continue
        if state == 0:
            # Simular recursión: hanoi(n-1, s, a, d) ; move s->d ; hanoi(n-1, a, d, s)
            stack.append((cur_n, s, d, a, 2))          # después de segundo bloque
            stack.append((cur_n, s, d, a, 1))          # movimiento central
            stack.append((cur_n - 1, s, a, d, 0))      # primer bloque
        elif state == 1:
            steps.append([s, d])  # usar lista para JSON compacto
        else:
            stack.append((cur_n - 1, a, d, s, 0))
    return steps

@app.route("/hanoi", methods=["POST"])
def hanoi():
    # Rechazar si no es JSON explícito
    if request.content_type is None or "application/json" not in request.content_type.lower():
        # Reglas del usuario: devolver arreglo vacío si inválido
        return jsonify([]), 200

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify([]), 200

    n = data.get("n")
    src = data.get("from", "A")
    dst = data.get("to", "C")
    aux = data.get("aux", "B")

    # Validaciones mínimas + límites
    if not isinstance(n, int) or n < 0 or n > MAX_N:
        return jsonify([]), 200
    if any(not isinstance(x, str) or not x for x in (src, dst, aux)):
        return jsonify([]), 200
    if len({src, dst, aux}) < 3:
        return jsonify([]), 200

    # n==0 => arreglo vacío (sin pasos)
    if n == 0:
        return jsonify([]), 200

    # Generación rápida (iterativa, sin recursion overhead)
    steps = hanoi_steps_iter(n, src, dst, aux)

    # Devolver directamente el arreglo de pasos, como solicitaste
    return jsonify(steps), 200

if __name__ == "__main__":
    # Modo dev: flask built-in; en Docker usaremos gunicorn
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), threaded=True)
