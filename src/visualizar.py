"""Genera las figuras y la tabla de estadísticas del informe.

Salida en figuras/:
- grafo_completo.png:      el almacén entero, coloreado por zona.
- subgrafo_zona_A/B/C.png: cada zona, coloreada por departamento.
- subgrafos_integrantes.png: las tres zonas en una sola figura.
- pedido_ejemplo.png:      un pedido real marcado sobre el almacén.
- mapa_demanda.png:        cuántas veces se pidió el producto de cada estante.
- tamano_pedidos.png:      cuántos productos tienen los pedidos reales.
- estadisticas.csv:        nodos, aristas y productos por zona.
- propiedades.csv:         propiedades generales del grafo.

Uso:
    python src/visualizar.py
"""

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.lines import Line2D

import config
from grafo import cargar_grafo

# Paleta categórica validada para daltonismo (orden fijo, nunca se recicla)
# y tintas neutras para lo que no es dato.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_TENUE = "#898781"
LINEA_TENUE = "#e1e0d9"
FONDO = "#fcfcfb"

# Rampa secuencial de un solo tono (azul) para magnitudes: claro = poco, oscuro = mucho.
RAMPA_AZUL = LinearSegmentedColormap.from_list(
    "azul", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])

COLOR_ZONA = dict(zip(config.ZONAS, SERIES))
ANCHO_FIGURA = 8      # pulgadas; a 200 ppp son 1600 px, el ancho de una página
PPP = 200

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 8,
    "axes.titlesize": 10,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "figure.facecolor": FONDO,
    "axes.facecolor": FONDO,
    "savefig.facecolor": FONDO,
})


def posiciones(g: nx.Graph) -> dict:
    return {n: (d["x"], d["y"]) for n, d in g.nodes(data=True)}


def nodos_de_tipo(g: nx.Graph, tipo: str, zona: str | None = None) -> list:
    return [n for n, d in g.nodes(data=True)
            if d["tipo"] == tipo and (zona is None or d.get("zona") == zona)]


def miles(n: int) -> str:
    """2311 -> '2 311', separador de miles en español."""
    return f"{n:,}".replace(",", " ")


def dibujar_base(ax, g: nx.Graph, pos: dict, color_pasillo: str = TINTA_TENUE) -> None:
    """Aristas, puntos de pasillo, intersecciones y depósito, en tonos neutros."""
    nx.draw_networkx_edges(g, pos, ax=ax, edge_color=LINEA_TENUE, width=0.6)
    nx.draw_networkx_nodes(g, pos, ax=ax, nodelist=nodos_de_tipo(g, "pasillo"),
                           node_size=1.2, node_color=color_pasillo)
    nx.draw_networkx_nodes(g, pos, ax=ax, nodelist=nodos_de_tipo(g, "interseccion"),
                           node_size=6, node_color=TINTA_SECUNDARIA, node_shape="s")
    if "DEPOSITO" in g:
        nx.draw_networkx_nodes(g, pos, ax=ax, nodelist=["DEPOSITO"], node_size=60,
                               node_color=TINTA, node_shape="s")


def leyenda_estructura() -> list:
    return [
        Line2D([], [], ls="", marker="o", ms=2.5, color=TINTA_TENUE, label="Punto de pasillo"),
        Line2D([], [], ls="", marker="s", ms=3.5, color=TINTA_SECUNDARIA, label="Intersección"),
        Line2D([], [], ls="", marker="s", ms=6, color=TINTA, label="Depósito"),
    ]


def preparar_ejes(ax) -> None:
    ax.set_aspect("equal")
    ax.set_xlabel("metros", color=TINTA_TENUE)
    ax.tick_params(colors=TINTA_TENUE, labelsize=7, left=True, bottom=True,
                   labelleft=True, labelbottom=True)
    for lado, spine in ax.spines.items():
        spine.set_visible(lado in ("left", "bottom"))
        spine.set_color(LINEA_TENUE)


def guardar(fig, nombre: str) -> None:
    config.FIGURAS.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.FIGURAS / nombre, dpi=PPP, bbox_inches="tight")
    plt.close(fig)
    print(f"  figuras/{nombre}")


def figura_grafo_completo(g: nx.Graph) -> None:
    pos = posiciones(g)
    fig, ax = plt.subplots(figsize=(ANCHO_FIGURA, 3.4))
    dibujar_base(ax, g, pos)

    handles = []
    for zona, datos in config.ZONAS.items():
        estantes = nodos_de_tipo(g, "estante", zona)
        nx.draw_networkx_nodes(g, pos, ax=ax, nodelist=estantes, node_size=2.5,
                               node_color=COLOR_ZONA[zona])
        xs = [pos[n][0] for n in estantes]
        ax.text((min(xs) + max(xs)) / 2, max(p[1] for p in pos.values()) + 2.5,
                f"Zona {zona} · {datos['nombre']}", ha="center", color=TINTA, fontsize=8)
        handles.append(Line2D([], [], ls="", marker="o", ms=4, color=COLOR_ZONA[zona],
                              label=f"Estante zona {zona}"))

    ax.set_title(f"Grafo completo del almacén: {miles(g.number_of_nodes())} nodos, "
                 f"{miles(g.number_of_edges())} aristas", pad=18)
    ax.legend(handles=handles + leyenda_estructura(), loc="upper center",
              bbox_to_anchor=(0.5, -0.22), ncol=6, frameon=False, fontsize=7)
    preparar_ejes(ax)
    guardar(fig, "grafo_completo.png")


def dibujar_subgrafo(ax, g: nx.Graph, zona: str, tam_estante: float = 9) -> None:
    """Dibuja la zona en `ax`, con los estantes coloreados por departamento."""
    datos = config.ZONAS[zona]
    nodos_zona = [n for n, d in g.nodes(data=True) if d.get("zona") == zona]
    sub = g.subgraph(nodos_zona)
    pos = posiciones(sub)
    dibujar_base(ax, sub, pos)

    handles = []
    for departamento, color in zip(datos["departamentos"], SERIES):
        estantes = [n for n in nodos_de_tipo(sub, "estante")
                    if sub.nodes[n].get("departamento") == departamento]
        if not estantes:
            continue
        nx.draw_networkx_nodes(sub, pos, ax=ax, nodelist=estantes, node_size=tam_estante,
                               node_color=color)
        nombre = config.DEPARTAMENTOS_ES[departamento]
        handles.append(Line2D([], [], ls="", marker="o", ms=5, color=color,
                              label=f"{nombre} ({len(estantes)})"))

    # Número de pasillo sobre cada uno.
    y_fondo = max(p[1] for p in pos.values())
    for pasillo in range(1, config.PASILLOS_POR_ZONA + 1):
        x = pos[f"{zona}{pasillo:02d}-00"][0]
        ax.text(x, y_fondo + 1.5, f"P{pasillo}", ha="center", color=TINTA_SECUNDARIA, fontsize=7)

    ax.set_title(f"Subgrafo {datos['responsable']} · Zona {zona} ({datos['nombre']}): "
                 f"{sub.number_of_nodes()} nodos, {sub.number_of_edges()} aristas", pad=16)
    ax.legend(handles=handles + leyenda_estructura()[:2], loc="center left",
              bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize=7,
              title="Ubicaciones por departamento", title_fontsize=7)
    preparar_ejes(ax)


def figura_subgrafo_zona(g: nx.Graph, zona: str) -> None:
    fig, ax = plt.subplots(figsize=(ANCHO_FIGURA, 5.2))
    dibujar_subgrafo(ax, g, zona)
    guardar(fig, f"subgrafo_zona_{zona}.png")


def figura_subgrafos(g: nx.Graph) -> None:
    """Los tres subgrafos en una sola figura, para ahorrar espacio en el informe."""
    fig, axes = plt.subplots(len(config.ZONAS), 1, figsize=(ANCHO_FIGURA, 9.6))
    for ax, zona in zip(axes, config.ZONAS):
        dibujar_subgrafo(ax, g, zona, tam_estante=4)
    fig.tight_layout(h_pad=1.5)
    guardar(fig, "subgrafos_integrantes.png")


def elegir_pedido_ejemplo(g: nx.Graph, pedidos: pd.DataFrame) -> pd.DataFrame:
    """El primer pedido de 8 a 12 productos que pasa por las tres zonas."""
    zona_de = {d["product_id"]: d["zona"] for _, d in g.nodes(data=True) if "product_id" in d}
    pedidos = pedidos.assign(zona=pedidos["product_id"].map(zona_de))
    resumen = pedidos.groupby("order_id").agg(n=("product_id", "size"), zonas=("zona", "nunique"))
    candidato = resumen[(resumen["n"].between(8, 12)) & (resumen["zonas"] == 3)].index[0]
    return pedidos[pedidos["order_id"] == candidato]


def figura_pedido(g: nx.Graph, pedidos: pd.DataFrame) -> None:
    pedido = elegir_pedido_ejemplo(g, pedidos)
    ubicacion_de = {d["product_id"]: n for n, d in g.nodes(data=True) if "product_id" in d}
    pos = posiciones(g)

    fig, ax = plt.subplots(figsize=(ANCHO_FIGURA, 3.4))
    dibujar_base(ax, g, pos, color_pasillo=LINEA_TENUE)
    nx.draw_networkx_nodes(g, pos, ax=ax, nodelist=nodos_de_tipo(g, "estante"),
                           node_size=1.5, node_color=LINEA_TENUE)

    puntos = [ubicacion_de[p] for p in pedido["product_id"]]
    nx.draw_networkx_nodes(g, pos, ax=ax, nodelist=puntos, node_size=36,
                           node_color=SERIES[0], edgecolors=FONDO, linewidths=1)
    for orden, nodo in enumerate(puntos, start=1):
        ax.annotate(str(orden), pos[nodo], xytext=(0, 5), textcoords="offset points",
                    ha="center", fontsize=6.5, color=TINTA, fontweight="bold")

    ax.set_title(f"Pedido real #{pedido['order_id'].iloc[0]}: {len(puntos)} productos "
                 f"en las 3 zonas (numerados en el orden del carrito)", pad=10)
    handles = [Line2D([], [], ls="", marker="o", ms=6, color=SERIES[0],
                      label="Producto del pedido")] + leyenda_estructura()[1:]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.22),
              ncol=4, frameon=False, fontsize=7)
    preparar_ejes(ax)
    guardar(fig, "pedido_ejemplo.png")

    tabla = pedido.assign(ubicacion=puntos,
                          producto=[g.nodes[n]["producto"] for n in puntos])
    tabla[["add_to_cart_order", "ubicacion", "zona", "producto"]].to_csv(
        config.FIGURAS / "pedido_ejemplo.csv", index=False)


def figura_mapa_demanda(g: nx.Graph, productos: pd.DataFrame) -> None:
    """Cada estante coloreado según cuántas veces se pidió su producto."""
    pos = posiciones(g)
    demanda = productos.set_index("ubicacion")["pedidos"]
    estantes = nodos_de_tipo(g, "estante")
    valores = [max(demanda.get(n, 1), 1) for n in estantes]

    fig, ax = plt.subplots(figsize=(ANCHO_FIGURA, 3.6))
    dibujar_base(ax, g, pos, color_pasillo=LINEA_TENUE)
    puntos = ax.scatter([pos[n][0] for n in estantes], [pos[n][1] for n in estantes],
                        s=4, c=valores, cmap=RAMPA_AZUL, zorder=3,
                        norm=LogNorm(vmin=min(valores), vmax=max(valores)))
    barra = fig.colorbar(puntos, ax=ax, orientation="horizontal", fraction=0.05, pad=0.2,
                         aspect=50)
    barra.set_label("Veces que se pidió el producto (escala logarítmica)", color=TINTA_SECUNDARIA)
    barra.ax.tick_params(labelsize=7, colors=TINTA_TENUE)
    barra.outline.set_visible(False)

    for zona, datos in config.ZONAS.items():
        xs = [pos[n][0] for n in nodos_de_tipo(g, "estante", zona)]
        ax.text((min(xs) + max(xs)) / 2, max(p[1] for p in pos.values()) + 2.5,
                f"Zona {zona} · {datos['nombre']}", ha="center", color=TINTA, fontsize=8)
    ax.set_title("Mapa de demanda: frecuencia con que se pide cada ubicación", pad=18)
    preparar_ejes(ax)
    guardar(fig, "mapa_demanda.png")


def figura_tamano_pedidos(pedidos: pd.DataFrame) -> None:
    """Histograma del número de productos por pedido."""
    tamanos = pedidos.groupby("order_id").size()
    conteo = tamanos.value_counts().sort_index()
    hasta_15 = (tamanos <= 15).mean()

    fig, ax = plt.subplots(figsize=(ANCHO_FIGURA, 3.2))
    ax.bar(conteo.index, conteo.values, width=0.8, color=SERIES[0])
    ax.axvline(15.5, color=TINTA_SECUNDARIA, lw=1, ls="--")
    ax.text(15.8, conteo.max() * 0.9,
            f"{hasta_15:.1%}".replace(".", ",") + " de los pedidos\ntiene 15 productos o menos",
            color=TINTA_SECUNDARIA, fontsize=7.5, va="top")
    ax.set_title(f"Tamaño de los {miles(len(tamanos))} pedidos reales", pad=10)
    ax.set_xlabel("Productos por pedido", color=TINTA_TENUE)
    ax.set_ylabel("Número de pedidos", color=TINTA_TENUE)
    ax.set_xticks(range(2, int(tamanos.max()) + 1, 2))
    ax.yaxis.grid(True, color=LINEA_TENUE, lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors=TINTA_TENUE, labelsize=7)
    for lado, spine in ax.spines.items():
        spine.set_visible(lado == "bottom")
        spine.set_color(LINEA_TENUE)
    guardar(fig, "tamano_pedidos.png")


def propiedades(g: nx.Graph) -> pd.DataFrame:
    """Propiedades generales del grafo y distancias desde el depósito."""
    grados = [d for _, d in g.degree()]
    distancia = nx.single_source_dijkstra_path_length(g, "DEPOSITO", weight="peso")
    a_estantes = [distancia[n] for n in nodos_de_tipo(g, "estante")]
    filas = [
        ("Vértices", miles(g.number_of_nodes())),
        ("Aristas", miles(g.number_of_edges())),
        ("Grado promedio", f"{sum(grados) / len(grados):.2f}"),
        ("Grado máximo", max(grados)),
        ("Vértices de grado 1 (estantes y depósito)", miles(grados.count(1))),
        ("Componentes conexas", nx.number_connected_components(g)),
        ("Suma de pesos de las aristas (m)", f"{g.size(weight='peso'):,.1f}".replace(",", " ")),
        ("Distancia media depósito-estante (m)", f"{sum(a_estantes) / len(a_estantes):.1f}"),
        ("Distancia máxima depósito-estante (m)", f"{max(a_estantes):.1f}"),
    ]
    tabla = pd.DataFrame(filas, columns=["propiedad", "valor"])
    tabla.to_csv(config.FIGURAS / "propiedades.csv", index=False)
    return tabla


def estadisticas(g: nx.Graph, pedidos: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for zona, datos in config.ZONAS.items():
        nodos = [n for n, d in g.nodes(data=True) if d.get("zona") == zona]
        sub = g.subgraph(nodos)
        tipos = pd.Series([g.nodes[n]["tipo"] for n in nodos]).value_counts()
        filas.append({
            "zona": f"{zona} · {datos['nombre']}",
            "nodos": len(nodos),
            "estantes": tipos.get("estante", 0),
            "puntos_pasillo": tipos.get("pasillo", 0),
            "intersecciones": tipos.get("interseccion", 0),
            "aristas_internas": sub.number_of_edges(),
            "departamentos": len(datos["departamentos"]),
        })
    total = pd.DataFrame(filas)
    fila_total = total.select_dtypes("number").sum()
    fila_total["zona"] = "Total (incluye depósito y enlaces entre zonas)"
    fila_total["nodos"] = g.number_of_nodes()
    fila_total["aristas_internas"] = g.number_of_edges()
    total = pd.concat([total, fila_total.to_frame().T], ignore_index=True)
    total.to_csv(config.FIGURAS / "estadisticas.csv", index=False)

    tamanos = pedidos.groupby("order_id").size()
    grados = [d for _, d in g.degree()]
    print(total.to_string(index=False))
    print(f"\nGrado promedio: {sum(grados) / len(grados):.2f}  ·  "
          f"conexo: {'sí' if nx.is_connected(g) else 'no'}")
    print(f"Pedidos: {len(tamanos):,}  ·  productos por pedido: "
          f"media {tamanos.mean():.1f}, mediana {tamanos.median():.0f}, máx. {tamanos.max()}")
    return total


def main() -> None:
    g = cargar_grafo()
    pedidos = pd.read_csv(config.DATA_PROCESSED / "pedidos.csv")
    productos = pd.read_csv(config.DATA_PROCESSED / "productos.csv")
    print("Figuras:")
    figura_grafo_completo(g)
    for zona in config.ZONAS:
        figura_subgrafo_zona(g, zona)
    figura_subgrafos(g)
    figura_pedido(g, pedidos)
    figura_mapa_demanda(g, productos)
    figura_tamano_pedidos(pedidos)
    print()
    estadisticas(g, pedidos)
    print()
    print(propiedades(g).to_string(index=False))


if __name__ == "__main__":
    main()
