"""Construye el grafo del almacén a partir de data/processed/productos.csv.

Tipos de nodo:
- deposito:     donde empieza y termina cada ruta de picking.
- interseccion: extremos de cada pasillo, unidos por los pasillos transversales.
- pasillo:      puntos por donde camina el picker, uno por posición.
- estante:      ubicación de un producto, a la izquierda o derecha del pasillo.

Las aristas son no dirigidas y su peso es la distancia en metros.

Escribe data/processed/nodos.csv y data/processed/aristas.csv.

Uso:
    python src/grafo.py
"""

import networkx as nx
import pandas as pd

import config

ZONAS = list(config.ZONAS)
POSICION_FONDO = config.POSICIONES_POR_PASILLO + 1


def id_punto(zona: str, pasillo: int, posicion: int) -> str:
    """Punto del pasillo. La posición 0 es la intersección del frente y la
    última (POSICION_FONDO) la del fondo."""
    return f"{zona}{pasillo:02d}-{posicion:02d}"


def coordenada_x(zona: str, pasillo: int) -> float:
    """Centro del pasillo. Las zonas están una al lado de la otra."""
    indice_global = ZONAS.index(zona) * config.PASILLOS_POR_ZONA + (pasillo - 1)
    return indice_global * config.SEPARACION_PASILLOS


def construir_grafo(productos: pd.DataFrame) -> nx.Graph:
    g = nx.Graph()
    en_estante = productos.set_index("ubicacion")
    distancia_al_estante = config.ANCHO_PASILLO / 2
    desfase_estante = config.ANCHO_PASILLO / 2 + config.PROFUNDIDAD_ESTANTE / 2

    for zona in ZONAS:
        for pasillo in range(1, config.PASILLOS_POR_ZONA + 1):
            x = coordenada_x(zona, pasillo)

            # Recorrido del pasillo: frente, posiciones 1..N, fondo.
            for posicion in range(POSICION_FONDO + 1):
                extremo = posicion in (0, POSICION_FONDO)
                g.add_node(id_punto(zona, pasillo, posicion),
                           tipo="interseccion" if extremo else "pasillo",
                           zona=zona, pasillo=pasillo, posicion=posicion,
                           x=x, y=posicion * config.LARGO_POSICION)
                if posicion > 0:
                    g.add_edge(id_punto(zona, pasillo, posicion - 1),
                               id_punto(zona, pasillo, posicion),
                               peso=config.LARGO_POSICION)

            # Estantes a ambos lados de cada posición.
            for posicion in range(1, config.POSICIONES_POR_PASILLO + 1):
                for lado, signo in (("I", -1), ("D", 1)):
                    ubicacion = f"{id_punto(zona, pasillo, posicion)}-{lado}"
                    datos = {}
                    if ubicacion in en_estante.index:
                        fila = en_estante.loc[ubicacion]
                        datos = {"product_id": int(fila["product_id"]),
                                 "producto": fila["product_name"],
                                 "departamento": fila["department"]}
                    g.add_node(ubicacion, tipo="estante", zona=zona, pasillo=pasillo,
                               posicion=posicion, lado=lado,
                               x=x + signo * desfase_estante,
                               y=posicion * config.LARGO_POSICION, **datos)
                    g.add_edge(ubicacion, id_punto(zona, pasillo, posicion),
                               peso=distancia_al_estante)

    # Pasillos transversales: unen las intersecciones vecinas, al frente y al fondo,
    # también entre zonas contiguas.
    pasillos = [(z, p) for z in ZONAS for p in range(1, config.PASILLOS_POR_ZONA + 1)]
    for (z1, p1), (z2, p2) in zip(pasillos, pasillos[1:]):
        for posicion in (0, POSICION_FONDO):
            g.add_edge(id_punto(z1, p1, posicion), id_punto(z2, p2, posicion),
                       peso=config.SEPARACION_PASILLOS)

    # Depósito frente al pasillo central del almacén.
    zona_central, pasillo_central = pasillos[len(pasillos) // 2]
    x_central = coordenada_x(zona_central, pasillo_central)
    g.add_node("DEPOSITO", tipo="deposito", x=x_central, y=-config.DISTANCIA_DEPOSITO)
    g.add_edge("DEPOSITO", id_punto(zona_central, pasillo_central, 0),
               peso=config.DISTANCIA_DEPOSITO)
    return g


def cargar_grafo() -> nx.Graph:
    """Reconstruye el grafo desde los CSV de data/processed/."""
    enteros = {"pasillo": "Int64", "posicion": "Int64", "product_id": "Int64"}
    nodos = pd.read_csv(config.DATA_PROCESSED / "nodos.csv", dtype=enteros)
    aristas = pd.read_csv(config.DATA_PROCESSED / "aristas.csv")
    g = nx.Graph()
    for fila in nodos.to_dict("records"):
        # Cada nodo guarda solo los atributos de su tipo (sin celdas vacías).
        g.add_node(fila.pop("id"), **{k: v for k, v in fila.items() if not pd.isna(v)})
    for origen, destino, peso in aristas.itertuples(index=False):
        g.add_edge(origen, destino, peso=peso)
    return g


def guardar_grafo(g: nx.Graph) -> None:
    nodos = pd.DataFrame([{"id": n, **d} for n, d in g.nodes(data=True)])
    columnas = ["id", "tipo", "zona", "pasillo", "posicion", "lado", "x", "y",
                "product_id", "producto", "departamento"]
    nodos = nodos[columnas].astype({"pasillo": "Int64", "posicion": "Int64", "product_id": "Int64"})
    aristas = pd.DataFrame([(u, v, d["peso"]) for u, v, d in g.edges(data=True)],
                           columns=["origen", "destino", "peso"])
    nodos.to_csv(config.DATA_PROCESSED / "nodos.csv", index=False)
    aristas.to_csv(config.DATA_PROCESSED / "aristas.csv", index=False)


def main() -> None:
    productos = pd.read_csv(config.DATA_PROCESSED / "productos.csv")
    g = construir_grafo(productos)
    guardar_grafo(g)
    print(f"Grafo: {g.number_of_nodes():,} nodos y {g.number_of_edges():,} aristas")


if __name__ == "__main__":
    main()
