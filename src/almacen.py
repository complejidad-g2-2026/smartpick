"""Carga el almacén desde data/processed/ sin librerías de grafos.

lag   = {'A01-01': {'A01-00': 1.2, 'A01-02': 1.2, 'A01-01-I': 1.5, ...}, ...}
nodos = {'A01-01-I': {'tipo': 'estante', 'zona': 'A', 'x': -2.0, 'y': 1.2, ...}, ...}
"""

import csv
import os

import config


def cargar_almacen():
    nodos = {}
    with open(os.path.join(config.DATA_PROCESSED, "nodos.csv"), encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            nodo = {k: v for k, v in fila.items() if v != "" and k != "id"}
            nodo["x"], nodo["y"] = float(nodo["x"]), float(nodo["y"])
            for k in ("pasillo", "posicion", "product_id"):
                if k in nodo:
                    nodo[k] = int(nodo[k])
            nodos[fila["id"]] = nodo

    lag = {n: {} for n in nodos}
    with open(os.path.join(config.DATA_PROCESSED, "aristas.csv"), encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            peso = float(fila["peso"])
            lag[fila["origen"]][fila["destino"]] = peso
            lag[fila["destino"]][fila["origen"]] = peso
    return lag, nodos


def cargar_pedidos(nodos):
    """{order_id: [ubicaciones en el orden del carrito]}"""
    ubicacion_de = {d["product_id"]: n for n, d in nodos.items() if "product_id" in d}
    lineas = []
    with open(os.path.join(config.DATA_PROCESSED, "pedidos.csv"), encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            lineas.append((int(fila["order_id"]), int(fila["add_to_cart_order"]), int(fila["product_id"])))
    pedidos = {}
    for pedido, _, producto in sorted(lineas):
        pedidos.setdefault(pedido, []).append(ubicacion_de[producto])
    return pedidos
