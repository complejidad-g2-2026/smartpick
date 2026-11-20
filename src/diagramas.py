"""Genera los diagramas de la sección "Diseño del aplicativo" del informe.

Salida en figuras/:
- arquitectura.png: módulos de la aplicación y cómo se pasan los datos.
- flujo.png:        diagrama de flujo de una consulta de ruta.
- interfaz.png:     boceto de la interfaz gráfica, con la ruta óptima del
                    pedido de ejemplo dibujada sobre el almacén.

Uso:
    python src/diagramas.py
"""

from itertools import permutations

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

import config
from grafo import cargar_grafo
from visualizar import (FONDO, LINEA_TENUE, SERIES, TINTA, TINTA_SECUNDARIA,
                        TINTA_TENUE, dibujar_base, guardar, nodos_de_tipo, posiciones)

AZUL, NARANJA = SERIES[0], SERIES[1]
CAJA = "#ffffff"
OSCURO = "#14213D"


def caja(ax, x, y, w, h, titulo, lineas=(), color=AZUL, relleno=CAJA):
    """Rectángulo redondeado con un título y líneas de texto debajo."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor=relleno, edgecolor=color, linewidth=1.6))
    ax.text(x + w / 2, y + h - 0.32, titulo, ha="center", va="top",
            fontsize=9, fontweight="bold", color=color)
    for i, linea in enumerate(lineas):
        ax.text(x + w / 2, y + h - 0.85 - i * 0.38, linea, ha="center", va="top",
                fontsize=7.5, color=TINTA_SECUNDARIA)


def flecha(ax, origen, destino, texto=None, lado="arriba"):
    ax.add_patch(FancyArrowPatch(origen, destino, arrowstyle="-|>", mutation_scale=12,
                                 color=TINTA_SECUNDARIA, linewidth=1.2))
    if texto:
        x, y = (origen[0] + destino[0]) / 2, (origen[1] + destino[1]) / 2
        dy = 0.18 if lado == "arriba" else -0.18
        ax.text(x, y + dy, texto, ha="center", va="bottom" if dy > 0 else "top",
                fontsize=7, color=TINTA_TENUE)


def lienzo(ancho, alto, xmax, ymax, titulo):
    fig, ax = plt.subplots(figsize=(ancho, alto))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.axis("off")
    ax.set_title(titulo, pad=8)
    return fig, ax


def diagrama_arquitectura() -> None:
    fig, ax = lienzo(8, 3.9, 16, 7.8, "Arquitectura de SmartPick: módulos y flujo de datos")

    caja(ax, 0.2, 3.0, 3.4, 2.6, "1. Datos", ["dataset.py", "Instacart (CSV)",
                                               "→ productos, pedidos"])
    caja(ax, 4.3, 3.0, 3.4, 2.6, "2. Grafo", ["grafo.py", "lista de adyacencia",
                                               "2 311 nodos · 2 339 aristas"])
    caja(ax, 8.4, 3.0, 3.4, 2.6, "3. Algoritmos", ["algoritmos/", "Dijkstra · Held-Karp",
                                                    "voraz · backtracking · S"],
         color=NARANJA)
    caja(ax, 12.5, 3.0, 3.3, 2.6, "4. Interfaz", ["gui.py (Tkinter)", "elegir pedido",
                                                   "ver ruta y comparar"])
    flecha(ax, (3.6, 4.3), (4.3, 4.3))
    flecha(ax, (7.7, 4.3), (8.4, 4.3))
    flecha(ax, (11.8, 4.3), (12.5, 4.3))

    caja(ax, 4.3, 0.2, 7.5, 1.9, "Evaluación (experimentos.py)",
         ["Corre cada técnica sobre una muestra de pedidos reales",
          "y registra distancia, tiempo y brecha frente a la óptima"], color=TINTA_SECUNDARIA)
    flecha(ax, (10.1, 3.0), (10.1, 2.1))
    flecha(ax, (6.0, 3.0), (6.0, 2.1))

    ax.text(8.0, 6.6, "config.py: parámetros del almacén (pasillos, distancias, zonas), "
            "usados por todos los módulos", ha="center", fontsize=7.5, color=TINTA_TENUE)
    guardar(fig, "arquitectura.png")


def rombo(ax, cx, cy, w, h, texto):
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2),
                          (cx - w / 2, cy)], closed=True, facecolor=CAJA,
                         edgecolor=NARANJA, linewidth=1.6))
    ax.text(cx, cy, texto, ha="center", va="center", fontsize=8, color=TINTA)


def paso(ax, cx, cy, texto, w=6.4, h=0.75, color=AZUL, relleno=CAJA):
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor=relleno, edgecolor=color, linewidth=1.5))
    ax.text(cx, cy, texto, ha="center", va="center", fontsize=8,
            color="#ffffff" if relleno != CAJA else TINTA)


def diagrama_flujo() -> None:
    fig, ax = lienzo(8, 6.6, 16, 16.6, "Diagrama de flujo: cálculo de la ruta de un pedido")
    ax.set_ylim(3.0, 16.6)
    cx = 5.2
    y = [16.0, 14.8, 13.6, 12.4, 11.2, 9.6, 7.6, 6.0, 4.8, 3.6]
    cx = 5.6

    paso(ax, cx, y[0], "Inicio", w=2.4, color=OSCURO, relleno=OSCURO)
    paso(ax, cx, y[1], "Cargar grafo y pedidos (CSV)")
    paso(ax, cx, y[2], "El usuario elige un pedido (n productos)")
    paso(ax, cx, y[3], "Dijkstra desde el depósito y cada producto")
    paso(ax, cx, y[4], "Matriz de distancias (n+1) × (n+1)")
    rombo(ax, cx, y[5], 3.6, 1.6, "¿n ≤ 15?")
    paso(ax, 2.2, y[6], "Held-Karp (óptima)", w=3.8, color=NARANJA)
    paso(ax, 9.0, y[6], "Vecino más cercano", w=3.8, color=NARANJA)
    paso(ax, cx, y[7], "Comparar: voraz · backtracking · recorrido en S", w=7.6)
    paso(ax, cx, y[8], "Mostrar ruta en el grafo y tabla de resultados", w=7.6)
    paso(ax, cx, y[9], "Fin", w=2.4, color=OSCURO, relleno=OSCURO)

    for a, b in [(0, 1), (1, 2), (2, 3), (3, 4)]:
        flecha(ax, (cx, y[a] - 0.38), (cx, y[b] + 0.38))
    flecha(ax, (cx, y[4] - 0.38), (cx, y[5] + 0.8))
    flecha(ax, (cx - 1.8, y[5]), (2.2, y[6] + 0.38), "sí")
    flecha(ax, (cx + 1.8, y[5]), (9.0, y[6] + 0.38), "no")
    flecha(ax, (2.2, y[6] - 0.38), (cx - 1.5, y[7] + 0.38))
    flecha(ax, (9.0, y[6] - 0.38), (cx + 1.5, y[7] + 0.38))
    flecha(ax, (cx, y[7] - 0.38), (cx, y[8] + 0.38))
    flecha(ax, (cx, y[8] - 0.38), (cx, y[9] + 0.38))

    notas = [
        (y[3], "O((V + E) log V) por ejecución"),
        (y[4], "Reduce 2 311 nodos a n + 1 puntos"),
        (y[5], "99,4 % de los pedidos reales"),
        (y[7], "Backtracking solo si n ≤ 10"),
    ]
    for yy, texto in notas:
        ax.text(12.0, yy, texto, va="center", fontsize=7.5, color=TINTA_TENUE)
    guardar(fig, "flujo.png")


def ruta_optima(g: nx.Graph, puntos: list) -> list:
    """Orden óptimo por fuerza bruta (solo para dibujar el boceto)."""
    dist = {p: nx.single_source_dijkstra_path_length(g, p, weight="peso")
            for p in ["DEPOSITO", *puntos]}

    def largo(r):
        t = ["DEPOSITO", *r, "DEPOSITO"]
        return sum(dist[a][b] for a, b in zip(t, t[1:]))

    mejor = min(permutations(puntos), key=largo)
    return ["DEPOSITO", *mejor, "DEPOSITO"], largo(mejor)


def boceto_interfaz() -> None:
    g = cargar_grafo()
    puntos = list(pd.read_csv(config.FIGURAS / "pedido_ejemplo.csv")["ubicacion"])
    orden, _ = ruta_optima(g, puntos)
    camino = []
    for a, b in zip(orden, orden[1:]):
        tramo = nx.shortest_path(g, a, b, weight="peso")
        camino.extend(tramo if not camino else tramo[1:])
    pos = posiciones(g)

    fig = plt.figure(figsize=(8, 5.2))
    fig.suptitle("Boceto de la interfaz gráfica de SmartPick", x=0.02, ha="left",
                 fontsize=10, fontweight="bold")

    # Panel de controles (izquierda).
    panel = fig.add_axes([0.02, 0.06, 0.24, 0.84])
    panel.set_xlim(0, 10)
    panel.set_ylim(0, 20)
    panel.axis("off")
    panel.add_patch(FancyBboxPatch((0, 0), 10, 20, boxstyle="round,pad=0,rounding_size=0.4",
                                   facecolor="#eef1f6", edgecolor=LINEA_TENUE))
    panel.text(0.6, 19, "Pedido", fontsize=8, fontweight="bold", color=TINTA)
    panel.add_patch(FancyBboxPatch((0.6, 17.2), 8.8, 1.2, boxstyle="round,pad=0,rounding_size=0.2",
                                   facecolor=CAJA, edgecolor=TINTA_TENUE))
    panel.text(1.0, 17.8, "#1682 · 8 productos   ▾", va="center", fontsize=7.5, color=TINTA)
    panel.text(0.6, 16.0, "Técnicas", fontsize=8, fontweight="bold", color=TINTA)
    for i, t in enumerate(["Held-Karp", "Vecino más cercano", "Backtracking", "Recorrido en S"]):
        yy = 14.8 - i * 1.3
        panel.add_patch(FancyBboxPatch((0.6, yy - 0.35), 0.7, 0.7, boxstyle="round,pad=0,rounding_size=0.1",
                                       facecolor=AZUL, edgecolor=AZUL))
        panel.text(1.7, yy, t, va="center", fontsize=7.5, color=TINTA)
    panel.add_patch(FancyBboxPatch((0.6, 8.2), 8.8, 1.4, boxstyle="round,pad=0,rounding_size=0.3",
                                   facecolor=NARANJA, edgecolor=NARANJA))
    panel.text(5.0, 8.9, "Calcular ruta", ha="center", va="center", fontsize=8.5,
               fontweight="bold", color="#ffffff")
    panel.text(0.6, 6.8, "Productos del pedido", fontsize=8, fontweight="bold", color=TINTA)
    nombres = ["Bathroom Tissue", "Organic Yellow Onion", "Peanut Butter", "Chicken Broth",
               "Beef Broth", "Romaine Lettuce", "Organic Lemon", "Vine Ripe Tomatoes"]
    for i, n in enumerate(nombres):
        panel.text(0.6, 5.9 - i * 0.7, f"{i + 1}. {n}", fontsize=6.5, color=TINTA_SECUNDARIA)

    # Vista del almacén con la ruta (arriba a la derecha).
    vista = fig.add_axes([0.29, 0.36, 0.69, 0.54])
    dibujar_base(vista, g, pos, color_pasillo=LINEA_TENUE)
    nx.draw_networkx_nodes(g, pos, ax=vista, nodelist=nodos_de_tipo(g, "estante"),
                           node_size=0.8, node_color=LINEA_TENUE)
    xs, ys = zip(*[pos[n] for n in camino])
    vista.plot(xs, ys, color=NARANJA, linewidth=1.6, zorder=4)
    nx.draw_networkx_nodes(g, pos, ax=vista, nodelist=puntos, node_size=22,
                           node_color=AZUL, edgecolors=FONDO, linewidths=0.8)
    vista.set_aspect("equal")
    vista.axis("off")
    vista.set_title("Ruta óptima sobre el almacén", fontsize=8, loc="left")

    # Tabla de resultados (abajo a la derecha).
    tabla = fig.add_axes([0.29, 0.06, 0.69, 0.26])
    tabla.axis("off")
    filas = [["Técnica", "Distancia", "Tiempo", "Brecha vs. óptima"],
             ["Held-Karp", "434,0 m", "por medir", "0 %"],
             ["Vecino más cercano", "452,8 m", "por medir", "+4,3 %"],
             ["Backtracking", "434,0 m", "por medir", "0 %"],
             ["Recorrido en S", "por medir", "por medir", "por medir"],
             ["Orden del carrito", "594,8 m", "—", "+37,0 %"]]
    t = tabla.table(cellText=filas, loc="center", cellLoc="left", colWidths=[0.34, 0.2, 0.18, 0.28])
    t.auto_set_font_size(False)
    t.set_fontsize(7.5)
    t.scale(1, 1.1)
    for (r, _), celda in t.get_celld().items():
        celda.set_edgecolor(LINEA_TENUE)
        if r == 0:
            celda.set_text_props(fontweight="bold", color=TINTA)
            celda.set_facecolor("#eef1f6")
    guardar(fig, "interfaz.png")


def main() -> None:
    print("Figuras:")
    diagrama_arquitectura()
    diagrama_flujo()
    boceto_interfaz()


if __name__ == "__main__":
    main()
