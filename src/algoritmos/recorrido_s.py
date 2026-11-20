"""Recorrido en "S" (método de referencia, no es una optimización).

El operario entra, de izquierda a derecha, a cada pasillo con algún producto
del pedido y lo recorre completo, alternando el sentido. Si le toca subir por
el último pasillo, recoge sus productos y vuelve por el mismo pasillo.

Complejidad: O(n log n), por el ordenamiento.
"""

import config

ZONAS = list(config.ZONAS)
FONDO = config.POSICIONES_POR_PASILLO + 1


def recorrido_s(nodos, ubicaciones):
    """Devuelve (orden de los productos, puntos de paso con la salida de cada pasillo)."""
    por_pasillo = {}
    for u in ubicaciones:
        d = nodos[u]
        indice = ZONAS.index(d["zona"]) * config.PASILLOS_POR_ZONA + d["pasillo"]
        por_pasillo.setdefault(indice, []).append(u)

    pasillos = sorted(por_pasillo)
    orden, puntos, subiendo = [], [], True
    for i, p in enumerate(pasillos):
        productos = sorted(por_pasillo[p], key=lambda u: nodos[u]["posicion"], reverse=not subiendo)
        orden += productos
        puntos += productos
        ultimo = i == len(pasillos) - 1
        if not (ultimo and subiendo):
            d = nodos[productos[0]]
            extremo = FONDO if subiendo else 0
            puntos.append(f"{d['zona']}{d['pasillo']:02d}-{extremo:02d}")
            subiendo = not subiendo
    return orden, puntos
