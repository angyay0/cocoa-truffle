# app.py
import os
from flask import Flask, request, jsonify
from hanoi_solver import classic_hanoi_steps_iter

app = Flask(__name__)

# Limite seguro por defecto
MAX_N = int(os.getenv("MAX_N", "14"))  # 2^14-1 = 16383 pasos (JSON razonable)

@app.route("/api/hanoi", methods=["POST"])
def hanoi():
    # Rechazar si no es JSON explicito para evitar inyecciones
    if request.content_type is None or "application/json" not in request.content_type.lower():
        # devolver arreglo vacío si inválido
        return jsonify([]), 200

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify([]), 200
    
    # Obtencion de parametros del body json
    n = data.get("size")
    src = data.get("from", "A")
    dst = data.get("to", "C")
    aux = data.get("aux", "B")

    # Validaciones
    if not isinstance(n, int) or n < 0 or n > MAX_N:
        return jsonify([]), 200
    if any(not isinstance(x, str) or not x for x in (src, dst, aux)):
        return jsonify([]), 200
    if len({src, dst, aux}) < 3:
        return jsonify([]), 200

    # n==0 => arreglo vacio 
    if n == 0:
        return jsonify([]), 200

    # Generacion iterativa, sin overhead
    steps = classic_hanoi_steps_iter(n, src, dst, aux)

    # Devolver directamente el arreglo de pasos
    return jsonify(steps), 200

if __name__ == "__main__":
    # Modo dev: flask built-in
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), threaded=True)
