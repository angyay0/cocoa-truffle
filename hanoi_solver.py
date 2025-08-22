from functools import lru_cache

# El algoritmo para 3 pegs, el mecanismo clasico optimizado
def classic_hanoi_steps_iter(n: int, src: str, dst: str, aux: str):
    """Genera la secuencia de pasos como tuplas (from, to) de forma iterativa (sin recursión).
        Reduciento a la complejidad aproximada a (2^n)-1
    """
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

@lru_cache(maxsize=None)
def _min_moves(n: int, k: int) -> int:
    """# minimo de movimientos para Hanoi con k pegs."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    if k <= 3:
        return (1 << n) - 1  # 2^n - 1

    best = float("inf")
    for t in range(1, n):
        cand = 2 * _min_moves(t, k) + _min_moves(n - t, k - 1)
        if cand < best:
            best = cand
    return int(best)

@lru_cache(maxsize=None)
def _best_t(n: int, k: int) -> int:
    """Devuelve el t óptimo que minimiza movimientos para (n,k)."""
    if n <= 1 or k <= 3:
        return 1
    best_t, best_val = 1, float("inf")
    for t in range(1, n):
        val = 2 * _min_moves(t, k) + _min_moves(n - t, k - 1)
        if val < best_val:
            best_val, best_t = val, t
    return best_t

def _hanoi3_with_labels(n: int, src: str, dst: str, aux: str):
    """Hanoi clásico para 3 pegs (Clásico)"""
    return classic_hanoi_steps_iter(n, src, dst, aux)

def hanoi_frame_stewart(n: int, pegs: tuple, src: str, dst: str):
    """Genera pasos para Hanoi con K= len(pegs) varillas usando Frame–Stewart."""
    k = len(pegs)
    if n <= 0:
        return []
    if n == 1:
        return [[src, dst]]
    if k < 3:
        return []
    # Caso k==3: resolver directo
    if k == 3:
        aux = next(p for p in pegs if p not in (src, dst))
        return _hanoi3_with_labels(n, src, dst, aux)

    # k > 3
    t = _best_t(n, k)
    aux_pegs = [p for p in pegs if p not in (src, dst)]
    buffer_peg = aux_pegs[0]  # cualquiera sirve por simetría

    steps = []
    # 1) Mueve t discos de src -> buffer con k pegs
    steps += hanoi_frame_stewart(t, pegs, src, buffer_peg)

    # 2) Mueve n-t discos de src -> dst con k-1 pegs (excluyendo buffer)
    pegs_without_buffer = tuple(p for p in pegs if p != buffer_peg)
    steps += hanoi_frame_stewart(n - t, pegs_without_buffer, src, dst)

    # 3) Mueve t discos de buffer -> dst con k pegs
    steps += hanoi_frame_stewart(t, pegs, buffer_peg, dst)
    return steps
