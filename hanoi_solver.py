from functools import lru_cache

# El algoritmo para 3 pegs, el mecanismo clasico optimizado
def classic_hanoi_steps_iter(n: int, src: str, dst: str, aux: str, offset: int = 0):
    """Genera la secuencia de pasos como tuplas (from, to) de forma iterativa (sin recursión).
        Reduciento a la complejidad aproximada a (2^n)-1
    """
    # Pila: (n, src, dst, aux, state)
    # state 0 => expandir, state 1 => emitir movimiento, state 2 => expandir segunda mitad
    stack = [(n, src, dst, aux, 0, offset)]
    steps = []
    while stack:
        cur_n, s, d, a, state, base = stack.pop()
        if cur_n <= 0:
            continue
        if state == 0:
            # Simular recursión: hanoi(n-1, s, a, d) ; move s->d ; hanoi(n-1, a, d, s)
            stack.append((cur_n, s, d, a, 2, base))          # después de segundo bloque
            stack.append((cur_n, s, d, a, 1, base))          # movimiento central
            stack.append((cur_n - 1, s, a, d, 0, base))      # primer bloque
        elif state == 1:
            disk_number = base + cur_n
            steps.append([disk_number, s, d])  # usar lista para JSON compacto
        else:
            stack.append((cur_n - 1, a, d, s, 0, base))
    return steps

@lru_cache(maxsize=None)
def _min_moves(n: int, k: int) -> int:
    if n <= 0:
        return 0
    if n == 1:
        return 1
    if k <= 3:
        return (1 << n) - 1
    best = float("inf")
    for t in range(1, n):
        cand = 2 * _min_moves(t, k) + _min_moves(n - t, k - 1)
        if cand < best:
            best = cand
    return int(best)

@lru_cache(maxsize=None)
def _best_t(n: int, k: int) -> int:
    if n <= 1 or k <= 3:
        return 1
    best_t, best_val = 1, float("inf")
    for t in range(1, n):
        val = 2 * _min_moves(t, k) + _min_moves(n - t, k - 1)
        if val < best_val:
            best_val, best_t = val, t
    return best_t

# --- 3 varillas con etiqueta de disco (usa offset para que los IDs sean correctos en subproblemas) ---
def _hanoi3_with_labels(n: int, src: str, dst: str, aux: str, offset: int):
    return classic_hanoi_steps_iter(n, src, dst, aux, offset=offset)

# --- Frame–Stewart SIEMPRE devolviendo [disk, from, to] ---
def hanoi_frame_stewart(n: int, pegs: tuple, src: str, dst: str, offset: int = 0):
    """
    Genera pasos [disk, from, to] para Hanoi con K = len(pegs) usando Frame–Stewart.
    'offset' asegura que los discos de este subproblema son offset+1 .. offset+n.
    """
    k = len(pegs)
    if n <= 0:
        return []
    if n == 1:
        return [[offset + 1, src, dst]]          # 
    if k < 3:
        return []
    if k == 3:
        aux = next(p for p in pegs if p not in (src, dst))
        return _hanoi3_with_labels(n, src, dst, aux, offset) 

    # k > 3
    t = _best_t(n, k)
    aux_pegs = [p for p in pegs if p not in (src, dst)]
    buffer_peg = aux_pegs[0]

    steps = []
    # 1) mover los t discos pequeños (offset .. offset+t-1) a buffer con k pegs
    steps += hanoi_frame_stewart(t, pegs, src, buffer_peg, offset=offset)
    # 2) mover los n-t discos grandes (offset+t .. offset+n-1) a dst con k-1 pegs (sin buffer)
    pegs_without_buffer = tuple(p for p in pegs if p != buffer_peg)
    steps += hanoi_frame_stewart(n - t, pegs_without_buffer, src, dst, offset=offset + t)
    # 3) regresar los t  del buffer al destino con k pegs
    steps += hanoi_frame_stewart(t, pegs, buffer_peg, dst, offset=offset)
    return steps