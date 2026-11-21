"""Backtracking con poda: arma la ruta producto por producto y descarta las
rutas parciales que ya miden más que la mejor ruta encontrada.

La mejor ruta inicial es la del vecino más cercano.

Complejidad: O(n!) en el peor caso.
"""

from .vecino_mas_cercano import vecino_mas_cercano


def backtracking(D):
    """D: matriz de distancias (índice 0 = depósito).
    Devuelve (orden, distancia, rutas parciales exploradas)."""
    n = len(D) - 1
    orden, costo = vecino_mas_cercano(D)
    mejor = {"orden": orden, "costo": costo, "explorados": 0}

    def explorar(ruta, costo, pendientes):
        mejor["explorados"] += 1
        ultimo = ruta[-1] if ruta else 0
        if not pendientes:
            if costo + D[ultimo][0] < mejor["costo"]:
                mejor["costo"] = costo + D[ultimo][0]
                mejor["orden"] = ruta[:]
            return
        for k in sorted(pendientes, key=lambda k: D[ultimo][k]):
            nuevo = costo + D[ultimo][k]
            # Poda
            if nuevo + D[k][0] >= mejor["costo"]:
                continue
            pendientes.remove(k)
            ruta.append(k)
            explorar(ruta, nuevo, pendientes)
            ruta.pop()
            pendientes.add(k)

    explorar([], 0, set(range(1, n + 1)))
    return mejor["orden"], mejor["costo"], mejor["explorados"]
