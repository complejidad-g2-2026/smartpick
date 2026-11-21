"""Held-Karp (programación dinámica): orden de visita óptimo.

D es la matriz de distancias: el índice 0 es el depósito y 1..n los productos.
C[S][k] = distancia mínima para salir del depósito, visitar los productos del
subconjunto S (máscara de bits) y terminar en k.

    C[{k}][k] = D[0][k]
    C[S][k]   = mín sobre m en S−{k} de C[S−{k}][m] + D[m][k]
    óptimo    = mín sobre k de C[todos][k] + D[k][0]

Complejidad: O(n² · 2ⁿ) en tiempo y O(n · 2ⁿ) en memoria.
"""


def held_karp(D):
    """Devuelve (orden de los productos, distancia de la ruta óptima)."""
    n = len(D) - 1
    if n == 0:
        return [], 0
    INF = float("inf")
    total = 1 << n
    C = [[INF] * n for _ in range(total)]
    previo = [[-1] * n for _ in range(total)]
    for k in range(n):
        C[1 << k][k] = D[0][k + 1]

    for S in range(1, total):
        en_S = [m for m in range(n) if S & (1 << m)]
        for k in range(n):
            if S & (1 << k):
                continue
            mejor, mejor_m = INF, -1
            for m in en_S:
                valor = C[S][m] + D[m + 1][k + 1]
                if valor < mejor:
                    mejor, mejor_m = valor, m
            T = S | (1 << k)
            C[T][k] = mejor
            previo[T][k] = mejor_m

    todos = total - 1
    costo, k = min((C[todos][k] + D[k + 1][0], k) for k in range(n))

    # Reconstrucción del orden
    orden, S = [], todos
    while k != -1:
        orden.append(k + 1)
        k, S = previo[S][k], S ^ (1 << k)
    return orden[::-1], costo
