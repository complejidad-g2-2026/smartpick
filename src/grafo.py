"""Grafo del almacén, implementado sin librerías de grafos.

El grafo se guarda como lista de adyacencia (diccionario de diccionarios):

    lag   = {'A01-01': {'A01-00': 1.2, 'A01-02': 1.2, 'A01-01-I': 1.5, ...}, ...}
    nodos = {'A01-01-I': {'tipo': 'estante', 'zona': 'A', 'x': -2.0, 'y': 1.2, ...}, ...}

Tipos de nodo:
- deposito:     donde empieza y termina cada ruta de picking.
- interseccion: extremos de cada pasillo, unidos por los pasillos transversales.
- pasillo:      puntos por donde camina el picker, uno por posición.
- estante:      ubicación de un producto, a la izquierda o derecha del pasillo.

Las aristas son no dirigidas y su peso es la distancia en metros.

Uso (regenera data/processed/nodos.csv y aristas.csv desde productos.csv):
    python src/grafo.py
"""

import csv
from collections import deque

import config

ZONAS = list(config.ZONAS)
POSICION_FONDO = config.POSICIONES_POR_PASILLO + 1
COLUMNAS_NODO = ["id", "tipo", "zona", "pasillo", "posicion", "lado", "x", "y",
                 "product_id", "producto", "departamento"]


def id_punto(zona: str, pasillo: int, posicion: int) -> str:
    """Punto del pasillo, p. ej. 'A03-12'. La posición 0 es la intersección del
    frente y POSICION_FONDO la del fondo."""
    return f"{zona}{pasillo:02d}-{posicion:02d}"


def coordenada_x(zona: str, pasillo: int) -> float:
    """Centro del pasillo. Las zonas están una al lado de la otra."""
    indice = ZONAS.index(zona) * config.PASILLOS_POR_ZONA + (pasillo - 1)
    return indice * config.SEPARACION_PASILLOS


def leer_csv(nombre: str) -> list[dict]:
    """Filas de un CSV de data/processed/ como diccionarios."""
    with open(config.DATA_PROCESSED / nombre, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def construir_grafo(productos: list[dict]) -> tuple[dict, list]:
    """Devuelve (nodos, aristas): nodos = {id: atributos}, aristas = [(u, v, peso)]."""
    producto_en = {p["ubicacion"]: p for p in productos}
    nodos, aristas = {}, []
    al_estante = config.ANCHO_PASILLO / 2
    desfase_estante = config.ANCHO_PASILLO / 2 + config.PROFUNDIDAD_ESTANTE / 2

    for zona in ZONAS:
        for pasillo in range(1, config.PASILLOS_POR_ZONA + 1):
            x = coordenada_x(zona, pasillo)

            # Puntos del pasillo, del frente al fondo
            for posicion in range(POSICION_FONDO + 1):
                extremo = posicion in (0, POSICION_FONDO)
                nodos[id_punto(zona, pasillo, posicion)] = {
                    "tipo": "interseccion" if extremo else "pasillo", "zona": zona,
                    "pasillo": pasillo, "posicion": posicion,
                    "x": x, "y": round(posicion * config.LARGO_POSICION, 2)}
                if posicion > 0:
                    aristas.append((id_punto(zona, pasillo, posicion - 1),
                                    id_punto(zona, pasillo, posicion), config.LARGO_POSICION))

            # Estantes a ambos lados
            for posicion in range(1, config.POSICIONES_POR_PASILLO + 1):
                for lado, signo in (("I", -1), ("D", 1)):
                    ubicacion = f"{id_punto(zona, pasillo, posicion)}-{lado}"
                    nodo = {"tipo": "estante", "zona": zona, "pasillo": pasillo,
                            "posicion": posicion, "lado": lado,
                            "x": x + signo * desfase_estante,
                            "y": round(posicion * config.LARGO_POSICION, 2)}
                    if ubicacion in producto_en:
                        p = producto_en[ubicacion]
                        nodo.update(product_id=int(p["product_id"]), producto=p["product_name"],
                                    departamento=p["department"])
                    nodos[ubicacion] = nodo
                    aristas.append((ubicacion, id_punto(zona, pasillo, posicion), al_estante))

    # Pasillos transversales del frente y del fondo
    pasillos = [(z, p) for z in ZONAS for p in range(1, config.PASILLOS_POR_ZONA + 1)]
    for (z1, p1), (z2, p2) in zip(pasillos, pasillos[1:]):
        for posicion in (0, POSICION_FONDO):
            aristas.append((id_punto(z1, p1, posicion), id_punto(z2, p2, posicion),
                            config.SEPARACION_PASILLOS))

    # Depósito frente al pasillo central
    zona_central, pasillo_central = pasillos[len(pasillos) // 2]
    nodos["DEPOSITO"] = {"tipo": "deposito", "x": coordenada_x(zona_central, pasillo_central),
                         "y": -config.DISTANCIA_DEPOSITO}
    aristas.append(("DEPOSITO", id_punto(zona_central, pasillo_central, 0),
                    config.DISTANCIA_DEPOSITO))
    return nodos, aristas


def guardar_grafo(nodos: dict, aristas: list) -> None:
    with open(config.DATA_PROCESSED / "nodos.csv", "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS_NODO, lineterminator="\n")
        escritor.writeheader()
        for id_nodo, datos in nodos.items():
            escritor.writerow({"id": id_nodo, **datos})
    with open(config.DATA_PROCESSED / "aristas.csv", "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(["origen", "destino", "peso"])
        escritor.writerows(aristas)


def cargar_grafo() -> tuple[dict, dict]:
    """Lee nodos.csv y aristas.csv. Devuelve (lag, nodos)."""
    nodos = {}
    for fila in leer_csv("nodos.csv"):
        nodo = {k: v for k, v in fila.items() if v != "" and k != "id"}
        nodo["x"], nodo["y"] = float(nodo["x"]), float(nodo["y"])
        for k in ("pasillo", "posicion", "product_id"):
            if k in nodo:
                nodo[k] = int(nodo[k])
        nodos[fila["id"]] = nodo

    lag = {n: {} for n in nodos}
    for fila in leer_csv("aristas.csv"):
        peso = float(fila["peso"])
        lag[fila["origen"]][fila["destino"]] = peso
        lag[fila["destino"]][fila["origen"]] = peso
    return lag, nodos


def cargar_pedidos(nodos: dict) -> dict:
    """{order_id: [ubicaciones de sus productos, en el orden del carrito]}"""
    ubicacion_de = {d["product_id"]: n for n, d in nodos.items() if "product_id" in d}
    lineas = sorted((int(f["order_id"]), int(f["add_to_cart_order"]), int(f["product_id"]))
                    for f in leer_csv("pedidos.csv"))
    pedidos = {}
    for pedido, _, producto in lineas:
        pedidos.setdefault(pedido, []).append(ubicacion_de[producto])
    return pedidos


def numero_de_aristas(lag: dict, ids=None) -> int:
    """Aristas entre los nodos de `ids` (todo el grafo si es None)."""
    ids = set(lag) if ids is None else set(ids)
    return sum(1 for u in ids for v in lag[u] if v in ids) // 2


def componentes_conexas(lag: dict) -> int:
    """BFS: número de componentes conexas. Complejidad: O(V + E)."""
    visitados, componentes = set(), 0
    for inicio in lag:
        if inicio in visitados:
            continue
        componentes += 1
        visitados.add(inicio)
        cola = deque([inicio])
        while cola:
            u = cola.popleft()
            for v in lag[u]:
                if v not in visitados:
                    visitados.add(v)
                    cola.append(v)
    return componentes


def main() -> None:
    nodos, aristas = construir_grafo(leer_csv("productos.csv"))
    guardar_grafo(nodos, aristas)
    lag, _ = cargar_grafo()
    print(f"Grafo: {len(nodos):,} nodos y {len(aristas):,} aristas · "
          f"componentes conexas (BFS): {componentes_conexas(lag)}")


if __name__ == "__main__":
    main()
