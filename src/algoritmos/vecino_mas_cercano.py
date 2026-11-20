"""Vecino más cercano (técnica voraz): desde el depósito, ir siempre al
producto pendiente más cercano.

Complejidad: O(n²). No garantiza la ruta óptima.
"""


def longitud(D: list[list[float]], orden: list[int]) -> float:
    """Distancia de depósito -> orden -> depósito."""
    tramos = [0, *orden, 0]
    return sum(D[a][b] for a, b in zip(tramos, tramos[1:]))


def vecino_mas_cercano(D: list[list[float]]) -> tuple[list[int], float]:
    actual, pendientes, orden = 0, set(range(1, len(D))), []
    while pendientes:
        actual = min(pendientes, key=lambda k: D[actual][k])
        orden.append(actual)
        pendientes.remove(actual)
    return orden, longitud(D, orden)
