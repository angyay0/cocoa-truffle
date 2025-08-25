import os
import string
import time
from flask import Flask, request, jsonify
from hanoi_solver import hanoi_frame_stewart,_min_moves

app = Flask(__name__)

# Limite seguro por defecto, si se especifica en ambiente puede cambiar
MAX_N = int(os.getenv("MAX_N", "51"))  # 2^14-1 = 16383 pasos (JSON razonable)

# Modificación para soportar el algoritmo de Frame-Stewart
def _default_pegs(k: int):
    """Genera etiquetas por defecto: A, B, C, D, ..., Z, A1, B1, ... si no se especifica en el parametro."""
    base = list(string.ascii_uppercase)
    labels = []
    i = 0
    while len(labels) < k:
        if i < 26:
            labels.append(base[i])
        else:
            labels.append(base[i % 26] + str(i // 26))
        i += 1
    return labels

@app.route("/api/hanoi", methods=["POST"])
def hanoi():
    # Rechazar si no es JSON explicito para evitar inyecciones
    if request.content_type is None or "application/json" not in request.content_type.lower():
        # devolver arreglo vacío si inválido
        return jsonify([]), 200
    
    start = time.perf_counter()

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify([]), 200
    
    # Obtencion de parametros del body json
    n = data.get("size")
    k = data.get("k")
    pegs_input = data.get("pegs")  # lista de pegs, aqui podemos especificarlas para definir de origen a destino
    src = data.get("from") # desde donde
    dst = data.get("to") # hasta donde
    count_only = bool(data.get("countOnly", False)) # para escenarios 20 y 50 (50 no se puede calcular)

    # Validaciones
    if not isinstance(n, int) or n < 0 or n > MAX_N:
        return jsonify([]), 200
    
    # Derivar pegs finales
    if isinstance(pegs_input, list) and all(isinstance(p, str) and p for p in pegs_input):
        pegs_list = pegs_input
    else:
        if not isinstance(k, int) or k < 3 or k > 16:  # limite para operaciones en el json step
            return jsonify([]), 200
        pegs_list = _default_pegs(k)

    # Validar unicidad y longitud
    if len(pegs_list) < 3 or len(set(pegs_list)) != len(pegs_list):
        return jsonify([]), 200

    # Definir src/dst por defecto (primera y última)
    if not isinstance(src, str) or src not in pegs_list:
        src = pegs_list[0]
    if not isinstance(dst, str) or dst not in pegs_list or dst == src:
        dst = pegs_list[-1] if pegs_list[-1] != src else pegs_list[-2]

    # n==0 -> []
    if n == 0:
        return jsonify([]), 200
    
    if count_only or n > 20 :
        k_eff = len(pegs_list)
        total = _min_moves(n, k_eff)
        elapsed = (time.perf_counter() - start) * 1000  
        print(f"[LOG] /hanoi ejecutado en {elapsed:.2f} ms con disk={n} y torres={len(pegs_list)} count-only")
        return jsonify({"moves": int(total)}), 200

    steps = hanoi_frame_stewart(n, tuple(pegs_list), src, dst)

    elapsed = (time.perf_counter() - start) * 1000  
    print(f"[LOG] /hanoi ejecutado en {elapsed:.2f} ms con disk={n} y torres={len(pegs_list)}")

    return jsonify(steps), 200

if __name__ == "__main__":
    # Modo dev: flask built-in
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), threaded=True)

