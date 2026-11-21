"""Figuras y tablas del grafo y del dataset para el informe.

Salida en figuras/visualizacion/:
- grafo_completo.png:          el almacén entero, coloreado por zona.
- subgrafo_zona_A/B/C.png:     cada zona, coloreada por departamento.
- subgrafos_integrantes.png:   las tres zonas en una sola figura.
- pedido_ejemplo.png y .csv:   un pedido real marcado sobre el almacén.
- mapa_demanda.png:            cuántas veces se pidió el producto de cada estante.
- tamano_pedidos.png:          cuántos productos tienen los pedidos reales.
- estadisticas.csv:            nodos y aristas por zona.
- propiedades.csv:             propiedades generales del grafo.

Uso:
    python src/visualizar.py
"""

import csv
from collections import Counter

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.lines import Line2D

import config
from algoritmos.dijkstra import dijkstra
from estilo import (ANCHO_FIGURA, COLOR_ZONA, FONDO, LINEA_TENUE, SERIES, TINTA,
                    TINTA_SECUNDARIA, TINTA_TENUE, de_tipo, dibujar_almacen,
                    etiquetar_zonas, guardar, miles, preparar_ejes, puntos)
from grafo import cargar_grafo, cargar_pedidos, componentes_conexas, leer_csv, numero_de_aristas

SALIDA = config.FIG_VISUALIZACION

# Escala de azules para la demanda
RAMPA_AZUL = LinearSegmentedColormap.from_list(
    "azul", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])


def leyenda_estructura() -> list:
    return [
        Line2D([], [], ls="", marker="o", ms=2.5, color=TINTA_TENUE, label="Punto de pasillo"),
        Line2D([], [], ls="", marker="s", ms=3.5, color=TINTA_SECUNDARIA, label="Intersección"),
        Line2D([], [], ls="", marker="s", ms=6, color=TINTA, label="Depósito"),
    ]


def escribir_csv(nombre: str, columnas: list, filas: list) -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    with open(SALIDA / nombre, "w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f, lineterminator="\n")
        escritor.writerow(columnas)
        escritor.writerows(filas)
    print(f"  figuras/visualizacion/{nombre}")


def figura_grafo_completo(lag, nodos) -> None:
    fig, ax = plt.subplots(figsize=(ANCHO_FIGURA, 3.4))
    dibujar_almacen(ax, lag, nodos)
    handles = []
    for zona in config.ZONAS:
        puntos(ax, nodos, de_tipo(nodos, "estante", zona), s=2.5, color=COLOR_ZONA[zona], zorder=3)
        handles.append(Line2D([], [], ls="", marker="o", ms=4, color=COLOR_ZONA[zona],
                              label=f"Estante zona {zona}"))
    etiquetar_zonas(ax, nodos)
    ax.set_aspect("equal")
    ax.set_title(f"Grafo completo del almacén: {miles(len(nodos))} nodos, "
                 f"{miles(numero_de_aristas(lag))} aristas", pad=18)
    ax.legend(handles=handles + leyenda_estructura(), loc="upper center",
              bbox_to_anchor=(0.5, -0.22), ncol=6, frameon=False, fontsize=7)
    preparar_ejes(ax)
    guardar(fig, SALIDA, "grafo_completo.png")


def dibujar_subgrafo(ax, lag, nodos, zona: str, tam_estante: float = 9) -> None:
    """Dibuja la zona en `ax`, con los estantes coloreados por departamento."""
    datos = config.ZONAS[zona]
    ids = [n for n, d in nodos.items() if d.get("zona") == zona]
    dibujar_almacen(ax, lag, nodos, ids)

    handles = []
    estantes = de_tipo(nodos, "estante", zona)
    for departamento, color in zip(datos["departamentos"], SERIES):
        del_dep = [n for n in estantes if nodos[n].get("departamento") == departamento]
        if not del_dep:
            continue
        puntos(ax, nodos, del_dep, s=tam_estante, color=color, zorder=3)
        handles.append(Line2D([], [], ls="", marker="o", ms=5, color=color,
                              label=f"{config.DEPARTAMENTOS_ES[departamento]} ({len(del_dep)})"))

    # Número de pasillo
    y_fondo = max(nodos[n]["y"] for n in ids)
    for pasillo in range(1, config.PASILLOS_POR_ZONA + 1):
        x = nodos[f"{zona}{pasillo:02d}-00"]["x"]
        ax.text(x, y_fondo + 1.5, f"P{pasillo}", ha="center", color=TINTA_SECUNDARIA, fontsize=7)

    ax.set_aspect("equal")
    ax.set_title(f"Subgrafo {datos['responsable']} · Zona {zona} ({datos['nombre']}): "
                 f"{len(ids)} nodos, {numero_de_aristas(lag, ids)} aristas", pad=16)
    ax.legend(handles=handles + leyenda_estructura()[:2], loc="center left",
              bbox_to_anchor=(1.01, 0.5), frameon=False, fontsize=7,
              title="Ubicaciones por departamento", title_fontsize=7)
    preparar_ejes(ax)


def figura_subgrafo_zona(lag, nodos, zona: str) -> None:
    fig, ax = plt.subplots(figsize=(ANCHO_FIGURA, 5.2))
    dibujar_subgrafo(ax, lag, nodos, zona)
    guardar(fig, SALIDA, f"subgrafo_zona_{zona}.png")


def figura_subgrafos(lag, nodos) -> None:
    """Los tres subgrafos en una sola figura, para ahorrar espacio en el informe."""
    fig, axes = plt.subplots(len(config.ZONAS), 1, figsize=(ANCHO_FIGURA, 9.6))
    for ax, zona in zip(axes, config.ZONAS):
        dibujar_subgrafo(ax, lag, nodos, zona, tam_estante=4)
    fig.tight_layout(h_pad=1.5)
    guardar(fig, SALIDA, "subgrafos_integrantes.png")


def figura_pedido(lag, nodos, pedidos) -> None:
    """El pedido de ejemplo, numerado en el orden en que se agregó al carrito."""
    pedido = config.PEDIDO_EJEMPLO
    ubicaciones = pedidos[pedido]

    fig, ax = plt.subplots(figsize=(ANCHO_FIGURA, 3.4))
    dibujar_almacen(ax, lag, nodos, color_pasillo=LINEA_TENUE)
    puntos(ax, nodos, de_tipo(nodos, "estante"), s=1.5, color=LINEA_TENUE, zorder=2)
    puntos(ax, nodos, ubicaciones, s=36, color=SERIES[0], edgecolors=FONDO, linewidths=1, zorder=3)
    for orden, n in enumerate(ubicaciones, start=1):
        ax.annotate(str(orden), (nodos[n]["x"], nodos[n]["y"]), xytext=(0, 5),
                    textcoords="offset points", ha="center", fontsize=6.5, color=TINTA,
                    fontweight="bold")
    zonas = len({nodos[n]["zona"] for n in ubicaciones})
    ax.set_aspect("equal")
    ax.set_title(f"Pedido real #{pedido}: {len(ubicaciones)} productos en {zonas} zonas "
                 f"(numerados en el orden del carrito)", pad=10)
    handles = [Line2D([], [], ls="", marker="o", ms=6, color=SERIES[0],
                      label="Producto del pedido")] + leyenda_estructura()[1:]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.22),
              ncol=4, frameon=False, fontsize=7)
    preparar_ejes(ax)
    guardar(fig, SALIDA, "pedido_ejemplo.png")

    escribir_csv("pedido_ejemplo.csv", ["add_to_cart_order", "ubicacion", "zona", "producto"],
                 [(i, n, nodos[n]["zona"], nodos[n]["producto"])
                  for i, n in enumerate(ubicaciones, start=1)])


def figura_mapa_demanda(lag, nodos) -> None:
    """Cada estante coloreado según cuántas veces se pidió su producto."""
    demanda = {p["ubicacion"]: int(p["pedidos"]) for p in leer_csv("productos.csv")}
    estantes = de_tipo(nodos, "estante")
    valores = [max(demanda.get(n, 1), 1) for n in estantes]

    fig, ax = plt.subplots(figsize=(ANCHO_FIGURA, 3.6))
    dibujar_almacen(ax, lag, nodos, color_pasillo=LINEA_TENUE)
    mapa = puntos(ax, nodos, estantes, s=4, c=valores, cmap=RAMPA_AZUL, zorder=3,
                  norm=LogNorm(vmin=min(valores), vmax=max(valores)))
    barra = fig.colorbar(mapa, ax=ax, orientation="horizontal", fraction=0.05, pad=0.2, aspect=50)
    barra.set_label("Veces que se pidió el producto (escala logarítmica)", color=TINTA_SECUNDARIA)
    barra.ax.tick_params(labelsize=7, colors=TINTA_TENUE)
    barra.outline.set_visible(False)
    etiquetar_zonas(ax, nodos)
    ax.set_aspect("equal")
    ax.set_title("Mapa de demanda: frecuencia con que se pide cada ubicación", pad=18)
    preparar_ejes(ax)
    guardar(fig, SALIDA, "mapa_demanda.png")


def figura_tamano_pedidos(pedidos) -> None:
    """Histograma del número de productos por pedido."""
    tamanos = [len(u) for u in pedidos.values()]
    conteo = Counter(tamanos)
    hasta_limite = sum(t <= config.LIMITE_HELD_KARP for t in tamanos) / len(tamanos)

    fig, ax = plt.subplots(figsize=(ANCHO_FIGURA, 3.2))
    ax.bar(list(conteo), list(conteo.values()), width=0.8, color=SERIES[0])
    corte = config.LIMITE_HELD_KARP + 0.5
    ax.axvline(corte, color=TINTA_SECUNDARIA, lw=1, ls="--")
    ax.text(corte + 0.3, max(conteo.values()) * 0.9,
            f"{hasta_limite:.1%}".replace(".", ",") + " de los pedidos\n"
            f"tiene {config.LIMITE_HELD_KARP} productos o menos",
            color=TINTA_SECUNDARIA, fontsize=7.5, va="top")
    ax.set_title(f"Tamaño de los {miles(len(tamanos))} pedidos reales", pad=10)
    ax.set_xlabel("Productos por pedido", color=TINTA_TENUE)
    ax.set_ylabel("Número de pedidos", color=TINTA_TENUE)
    ax.set_xticks(range(2, max(tamanos) + 1, 2))
    ax.yaxis.grid(True, color=LINEA_TENUE, lw=0.6)
    ax.set_axisbelow(True)
    preparar_ejes(ax, etiqueta_x=None)
    ax.spines["left"].set_visible(False)
    guardar(fig, SALIDA, "tamano_pedidos.png")


def estadisticas(lag, nodos) -> None:
    """Nodos y aristas por zona."""
    filas, totales = [], Counter()
    for zona, datos in config.ZONAS.items():
        ids = [n for n, d in nodos.items() if d.get("zona") == zona]
        tipos = Counter(nodos[n]["tipo"] for n in ids)
        fila = [f"{zona} · {datos['nombre']}", len(ids), tipos["estante"], tipos["pasillo"],
                tipos["interseccion"], numero_de_aristas(lag, ids), len(datos["departamentos"])]
        filas.append(fila)
        totales.update(dict(enumerate(fila[1:])))
    filas.append(["Total (incluye depósito y enlaces entre zonas)", len(nodos), totales[1],
                  totales[2], totales[3], numero_de_aristas(lag), totales[5]])
    escribir_csv("estadisticas.csv", ["zona", "nodos", "estantes", "puntos_pasillo",
                                      "intersecciones", "aristas_internas", "departamentos"], filas)


def propiedades(lag, nodos) -> None:
    """Propiedades generales del grafo y distancias desde el depósito."""
    grados = [len(vecinos) for vecinos in lag.values()]
    distancia, _ = dijkstra(lag, "DEPOSITO")
    a_estantes = [distancia[n] for n in de_tipo(nodos, "estante")]
    suma_pesos = sum(p for u in lag for v, p in lag[u].items() if u < v)
    filas = [
        ("Vértices", miles(len(nodos))),
        ("Aristas", miles(numero_de_aristas(lag))),
        ("Grado promedio", f"{sum(grados) / len(grados):.2f}"),
        ("Grado máximo", max(grados)),
        ("Vértices de grado 1 (estantes y depósito)", miles(grados.count(1))),
        ("Componentes conexas (BFS)", componentes_conexas(lag)),
        ("Suma de pesos de las aristas (m)", f"{suma_pesos:,.1f}".replace(",", " ")),
        ("Distancia media depósito-estante (m)", f"{sum(a_estantes) / len(a_estantes):.1f}"),
        ("Distancia máxima depósito-estante (m)", f"{max(a_estantes):.1f}"),
    ]
    escribir_csv("propiedades.csv", ["propiedad", "valor"], filas)
    for nombre, valor in filas:
        print(f"    {nombre}: {valor}")


def main() -> None:
    lag, nodos = cargar_grafo()
    pedidos = cargar_pedidos(nodos)
    print("Figuras y tablas:")
    figura_grafo_completo(lag, nodos)
    for zona in config.ZONAS:
        figura_subgrafo_zona(lag, nodos, zona)
    figura_subgrafos(lag, nodos)
    figura_pedido(lag, nodos, pedidos)
    figura_mapa_demanda(lag, nodos)
    figura_tamano_pedidos(pedidos)
    estadisticas(lag, nodos)
    propiedades(lag, nodos)


if __name__ == "__main__":
    main()
