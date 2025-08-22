# El algoritmo para 3 pegs, el mecanismo clasico optimizado
def classic_hanoi_steps_iter(n: int, src: str, dst: str, aux: str):
    """Genera la secuencia de pasos como tuplas (from, to) de forma iterativa (sin recursión).
        Reduciento a la complejidad de (2^n)-1
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

