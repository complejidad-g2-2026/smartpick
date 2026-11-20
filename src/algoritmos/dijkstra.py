"""Dijkstra (técnica voraz) con heapq sobre la lista de adyacencia lag.

Complejidad: O((V + E) log V) por ejecución.
"""

import heapq


def dijkstra(lag, origen):
    dist = {origen: 0}
    previo = {origen: None}
    visitados = set()
    cola = [(0, origen)]
    while cola:
        d, u = heapq.heappop(cola)
        if u in visitados:
            continue
        visitados.add(u)
        for v, peso in lag[u].items():
            if d + peso < dist.get(v, float("inf")):
                dist[v] = d + peso
                previo[v] = u
                heapq.heappush(cola, (dist[v], v))
    return dist, previo


def camino(previo, destino):
    nodos = []
    while destino is not None:
        nodos.append(destino)
        destino = previo[destino]
    return nodos[::-1]


class Distancias:
    """Guarda el Dijkstra de cada punto para no repetirlo."""

    def __init__(self, lag):
        self.lag = lag
        self.calculados = {}

    def desde(self, origen):
        if origen not in self.calculados:
            self.calculados[origen] = dijkstra(self.lag, origen)
        return self.calculados[origen]

    def distancia(self, a, b):
        return self.desde(a)[0][b]

    def camino(self, a, b):
        return camino(self.desde(a)[1], b)

    def matriz(self, puntos):
        return [[self.distancia(a, b) for b in puntos] for a in puntos]
