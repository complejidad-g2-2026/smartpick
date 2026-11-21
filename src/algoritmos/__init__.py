"""Algoritmos de SmartPick.

resolver() calcula la ruta de un pedido con cada técnica:
1. Dijkstra desde el depósito y desde cada producto: matriz (n + 1) × (n + 1).
2. Orden de visita con Held-Karp, vecino más cercano, backtracking y recorrido
   en "S". El orden del carrito se incluye como referencia.

El tiempo de cada técnica es solo el del cálculo del orden de visita.
"""

import time

import config

from .backtracking import backtracking
from .dijkstra import Distancias
from .held_karp import held_karp
from .recorrido_s import recorrido_s
from .vecino_mas_cercano import longitud, vecino_mas_cercano

TECNICAS = ["Held-Karp", "Vecino más cercano", "Backtracking", "Recorrido en S", "Orden del carrito"]


class Resultado:
    """Ruta de un pedido calculada con una técnica."""

    def __init__(self, tecnica):
        self.tecnica = tecnica
        self.distancia = None
        self.tiempo_ms = None
        self.orden = []
        self.camino = []
        self.nota = ""

    @property
    def calculado(self):
        return self.distancia is not None


def medir(funcion):
    """Ejecuta funcion() y devuelve (resultado, milisegundos)."""
    inicio = time.perf_counter()
    salida = funcion()
    return salida, (time.perf_counter() - inicio) * 1000


def unir_caminos(distancias, puntos):
    """Camino completo depósito -> puntos -> depósito, nodo por nodo."""
    tramos = ["DEPOSITO", *puntos, "DEPOSITO"]
    nodos = ["DEPOSITO"]
    for a, b in zip(tramos, tramos[1:]):
        nodos += distancias.camino(a, b)[1:]
    return nodos


def resolver(lag, nodos, ubicaciones, tecnicas=TECNICAS):
    """Devuelve los resultados de cada técnica y el tiempo de Dijkstra en ms."""
    n = len(ubicaciones)
    distancias = Distancias(lag)
    puntos = ["DEPOSITO", *ubicaciones]
    D, tiempo_dijkstra = medir(lambda: distancias.matriz(puntos))

    resultados = []
    for tecnica in tecnicas:
        r = Resultado(tecnica)
        if tecnica == "Held-Karp":
            if n > config.LIMITE_HELD_KARP:
                r.nota = f"solo hasta {config.LIMITE_HELD_KARP} productos"
            else:
                (orden, r.distancia), r.tiempo_ms = medir(lambda: held_karp(D))
                r.orden = [puntos[k] for k in orden]
        elif tecnica == "Vecino más cercano":
            (orden, r.distancia), r.tiempo_ms = medir(lambda: vecino_mas_cercano(D))
            r.orden = [puntos[k] for k in orden]
        elif tecnica == "Backtracking":
            if n > config.LIMITE_BACKTRACKING:
                r.nota = f"solo hasta {config.LIMITE_BACKTRACKING} productos"
            else:
                (orden, r.distancia, explorados), r.tiempo_ms = medir(lambda: backtracking(D))
                r.orden = [puntos[k] for k in orden]
                r.nota = f"{explorados:,} rutas parciales".replace(",", " ")
        elif tecnica == "Recorrido en S":
            (r.orden, pasos), r.tiempo_ms = medir(lambda: recorrido_s(nodos, ubicaciones))
            tramos = ["DEPOSITO", *pasos, "DEPOSITO"]
            r.distancia = sum(distancias.distancia(a, b) for a, b in zip(tramos, tramos[1:]))
            r.camino = unir_caminos(distancias, pasos)
        elif tecnica == "Orden del carrito":
            r.orden = list(ubicaciones)
            r.distancia = longitud(D, list(range(1, n + 1)))
        if r.calculado and not r.camino:
            r.camino = unir_caminos(distancias, r.orden)
        resultados.append(r)
    return resultados, tiempo_dijkstra


def distancia_optima(resultados):
    """La de Held-Karp o backtracking si se calcularon; si no, la menor."""
    exactas = [r.distancia for r in resultados if r.tecnica in ("Held-Karp", "Backtracking") and r.calculado]
    calculadas = exactas or [r.distancia for r in resultados if r.calculado]
    return min(calculadas) if calculadas else None
