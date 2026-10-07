"""Cálculo preliminar de la sección 4.1 del informe TB1.

Compara, para el pedido de ejemplo (figuras/pedido_ejemplo.csv), tres órdenes
de visita:
- el orden en que el cliente agregó los productos al carrito,
- el vecino más cercano (voraz),
- la ruta óptima por fuerza bruta (todas las permutaciones).

Es solo una comprobación inicial: las distancias entre productos se toman de
NetworkX. Las implementaciones propias (Dijkstra, Held-Karp, backtracking) son
parte del TB2.

Uso:
    python src/ruta_preliminar.py
"""

from itertools import permutations

import networkx as nx
import pandas as pd

import config
from grafo import cargar_grafo


def longitud(ruta: list, distancia: dict) -> float:
    """Distancia de depósito -> ruta -> depósito."""
    tramos = ["DEPOSITO", *ruta, "DEPOSITO"]
    return sum(distancia[a][b] for a, b in zip(tramos, tramos[1:]))


def vecino_mas_cercano(puntos: list, distancia: dict) -> list:
    actual, pendientes, ruta = "DEPOSITO", set(puntos), []
    while pendientes:
        actual = min(pendientes, key=lambda p: distancia[actual][p])
        ruta.append(actual)
        pendientes.remove(actual)
    return ruta


def main() -> None:
    g = cargar_grafo()
    puntos = list(pd.read_csv(config.FIGURAS / "pedido_ejemplo.csv")["ubicacion"])
    distancia = {p: nx.single_source_dijkstra_path_length(g, p, weight="peso")
                 for p in ["DEPOSITO", *puntos]}

    carrito = longitud(puntos, distancia)
    voraz = longitud(vecino_mas_cercano(puntos, distancia), distancia)
    optima = min(longitud(list(r), distancia) for r in permutations(puntos))

    print(f"Productos del pedido: {len(puntos)}")
    print(f"Orden del carrito:   {carrito:7.1f} m")
    print(f"Vecino más cercano:  {voraz:7.1f} m  (+{voraz / optima - 1:.1%} sobre la óptima)")
    print(f"Ruta óptima:         {optima:7.1f} m  ({1 - optima / carrito:.1%} menos que el carrito)")


if __name__ == "__main__":
    main()
