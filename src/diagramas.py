"""Diagramas de la sección "Diseño del aplicativo" del informe.

Salida en figuras/diseno/:
- arquitectura.png: módulos de la aplicación y cómo se pasan los datos.
- flujo.png:        diagrama de flujo del cálculo de la ruta de un pedido.
- interfaz.png:     boceto de la interfaz, con los resultados reales del
                    pedido de ejemplo.

Uso:
    python src/diagramas.py
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

import config
from algoritmos import TECNICAS, distancia_optima, resolver
from estilo import (ANCHO_FIGURA, COLOR_TECNICA, FONDO, LINEA_TENUE, SERIES, TINTA,
                    TINTA_SECUNDARIA, TINTA_TENUE, de_tipo, dibujar_almacen, guardar,
                    metros, milisegundos, miles, puntos)
from grafo import cargar_grafo, cargar_pedidos, numero_de_aristas

SALIDA = config.FIG_DISENO
AZUL, NARANJA = SERIES[0], SERIES[1]
CAJA = "#ffffff"
GRIS_PANEL = "#eef1f6"
OSCURO = "#14213D"


def lienzo(ancho, alto, xmax, ymin, ymax, titulo):
    fig, ax = plt.subplots(figsize=(ancho, alto))
    ax.set_xlim(0, xmax)
    ax.set_ylim(ymin, ymax)
    ax.axis("off")
    ax.set_title(titulo, pad=8)
    return fig, ax


def caja(ax, x, y, w, h, titulo, lineas=(), color=AZUL):
    """Rectángulo redondeado con un título y líneas de texto debajo."""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor=CAJA, edgecolor=color, linewidth=1.6))
    ax.text(x + w / 2, y + h - 0.32, titulo, ha="center", va="top",
            fontsize=9, fontweight="bold", color=color)
    for i, linea in enumerate(lineas):
        ax.text(x + w / 2, y + h - 0.85 - i * 0.38, linea, ha="center", va="top",
                fontsize=7.5, color=TINTA_SECUNDARIA)


def paso(ax, cx, cy, texto, w=7.6, h=0.8, color=AZUL, relleno=CAJA):
    """Paso del diagrama de flujo, centrado en (cx, cy)."""
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor=relleno, edgecolor=color, linewidth=1.5))
    ax.text(cx, cy, texto, ha="center", va="center", fontsize=8,
            color="#ffffff" if relleno != CAJA else TINTA)


def rombo(ax, cx, cy, w, h, texto):
    ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2),
                          (cx - w / 2, cy)], closed=True, facecolor=CAJA,
                         edgecolor=NARANJA, linewidth=1.6))
    ax.text(cx, cy, texto, ha="center", va="center", fontsize=8, color=TINTA)


def flecha(ax, *puntos_ruta, texto=None):
    """Flecha que pasa por los puntos dados; la punta queda en el último."""
    for a, b in zip(puntos_ruta[:-2], puntos_ruta[1:-1]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=TINTA_SECUNDARIA, lw=1.2)
    ax.add_patch(FancyArrowPatch(puntos_ruta[-2], puntos_ruta[-1], arrowstyle="-|>",
                                 mutation_scale=12, color=TINTA_SECUNDARIA, linewidth=1.2))
    if texto:
        (x1, y1), (x2, y2) = puntos_ruta[0], puntos_ruta[1]
        ax.text((x1 + x2) / 2 + 0.15, (y1 + y2) / 2 + 0.12, texto, fontsize=7.5, color=TINTA_TENUE)


def diagrama_arquitectura(lag, nodos) -> None:
    fig, ax = lienzo(ANCHO_FIGURA, 3.9, 16, 0, 7.8, "Arquitectura de SmartPick: módulos y flujo de datos")

    caja(ax, 0.05, 3.0, 3.75, 2.6, "1. Datos", ["dataset.py", "Instacart (CSV)", "→ productos, pedidos"])
    caja(ax, 4.1, 3.0, 3.75, 2.6, "2. Grafo", ["grafo.py", "lista de adyacencia + BFS",
                                               f"{miles(len(nodos))} nodos · {miles(numero_de_aristas(lag))} aristas"])
    caja(ax, 8.15, 3.0, 3.75, 2.6, "3. Algoritmos", ["algoritmos/", "Dijkstra · Held-Karp",
                                                    "voraz · backtracking · S"], color=NARANJA)
    caja(ax, 12.2, 3.0, 3.75, 2.6, "4. Interfaz", ["gui.py (Tkinter)", "elegir pedido",
                                                   "ver ruta y comparar"])
    flecha(ax, (3.8, 4.3), (4.1, 4.3))
    flecha(ax, (7.85, 4.3), (8.15, 4.3))
    flecha(ax, (11.9, 4.3), (12.2, 4.3))

    caja(ax, 3.8, 0.2, 8.5, 1.9, "Evaluación (experimentos.py)",
         ["Corre cada técnica sobre una muestra de pedidos reales",
          "y registra distancia, tiempo y brecha frente a la óptima"], color=TINTA_SECUNDARIA)
    flecha(ax, (6.0, 3.0), (6.0, 2.1))
    flecha(ax, (10.1, 3.0), (10.1, 2.1))

    ax.text(8.0, 6.6, "config.py: parámetros del almacén y de los algoritmos · "
            "estilo.py: colores y dibujo comunes", ha="center", fontsize=7.5, color=TINTA_TENUE)
    guardar(fig, SALIDA, "arquitectura.png")


def diagrama_flujo() -> None:
    fig, ax = lienzo(ANCHO_FIGURA, 7.2, 18, 3.9, 18.0, "Diagrama de flujo: cálculo de la ruta de un pedido")
    cx, dx = 5.0, 11.6

    paso(ax, cx, 17.4, "Inicio", w=2.4, color=OSCURO, relleno=OSCURO)
    paso(ax, cx, 16.2, "Cargar grafo (lista de adyacencia) y pedidos")
    paso(ax, cx, 15.0, "Elegir un pedido (n productos) y las técnicas")
    paso(ax, cx, 13.7, "Dijkstra desde el depósito y cada producto\n→ matriz de distancias (n+1)×(n+1)", h=1.1)
    rombo(ax, cx, 11.6, 4.4, 2.0, "¿Quedan técnicas\npor calcular?")
    rombo(ax, dx, 11.6, 4.4, 2.0, "¿n dentro del\nlímite de la técnica?")
    paso(ax, dx, 9.3, "Calcular orden de\nvisita y distancia", w=4.0, h=1.1, color=NARANJA)
    paso(ax, 16.2, 9.3, "Marcar\n«no aplica»", w=2.8, h=1.1, color=TINTA_TENUE)
    paso(ax, cx, 7.0, "Tabla: distancia, tiempo y brecha vs. óptima")
    paso(ax, cx, 5.8, "Dibujar la ruta más corta sobre el almacén")
    paso(ax, cx, 4.6, "Fin", w=2.4, color=OSCURO, relleno=OSCURO)

    for y1, y2 in [(17.4, 16.2), (16.2, 15.0)]:
        flecha(ax, (cx, y1 - 0.4), (cx, y2 + 0.4))
    flecha(ax, (cx, 14.6), (cx, 14.25))
    flecha(ax, (cx, 13.15), (cx, 12.6))
    flecha(ax, (cx + 2.2, 11.6), (dx - 2.2, 11.6), texto="sí")
    flecha(ax, (dx, 10.6), (dx, 9.85), texto="sí")
    flecha(ax, (dx + 2.2, 11.6), (16.2, 11.6), (16.2, 9.85), texto="no")
    # Vuelta del ciclo
    flecha(ax, (dx, 8.75), (dx, 8.2), (9.3, 8.2), (9.3, 12.88), (cx + 0.05, 12.88))
    ax.plot([16.2, 16.2, dx], [8.75, 8.2, 8.2], color=TINTA_SECUNDARIA, lw=1.2)
    ax.text(9.45, 10.0, "siguiente\ntécnica", fontsize=7, color=TINTA_TENUE)
    flecha(ax, (cx, 10.6), (cx, 7.4), texto="no")
    flecha(ax, (cx, 6.6), (cx, 6.2))
    flecha(ax, (cx, 5.4), (cx, 5.0))

    notas = [
        "Complejidad de cada técnica:",
        "Dijkstra: O((V + E) log V) por ejecución",
        f"Held-Karp (PD): O(n²·2ⁿ), n ≤ {config.LIMITE_HELD_KARP}",
        f"Backtracking con poda: O(n!), n ≤ {config.LIMITE_BACKTRACKING}",
        "Vecino más cercano (voraz): O(n²)",
        "Recorrido en S (referencia): O(n log n)",
    ]
    for i, texto in enumerate(notas):
        ax.text(10.3, 7.3 - i * 0.48, texto, fontsize=7.5, va="center",
                color=TINTA_SECUNDARIA if i == 0 else TINTA_TENUE,
                fontweight="bold" if i == 0 else "normal")
    guardar(fig, SALIDA, "flujo.png")


def boceto_interfaz(lag, nodos, pedidos) -> None:
    pedido = config.PEDIDO_EJEMPLO
    ubicaciones = pedidos[pedido]
    resultados, _ = resolver(lag, nodos, ubicaciones)
    optima = distancia_optima(resultados)
    mejor = min((r for r in resultados if r.calculado), key=lambda r: r.distancia)

    fig = plt.figure(figsize=(ANCHO_FIGURA, 5.2))
    fig.suptitle("Boceto de la interfaz gráfica de SmartPick", x=0.02, ha="left",
                 fontsize=10, fontweight="bold")

    # Panel izquierdo
    panel = fig.add_axes([0.02, 0.06, 0.24, 0.84])
    panel.set_xlim(0, 10)
    panel.set_ylim(0, 20)
    panel.axis("off")
    panel.add_patch(FancyBboxPatch((0, 0), 10, 20, boxstyle="round,pad=0,rounding_size=0.4",
                                   facecolor=GRIS_PANEL, edgecolor=LINEA_TENUE))
    panel.text(0.6, 19, "Pedido", fontsize=8, fontweight="bold", color=TINTA)
    panel.add_patch(FancyBboxPatch((0.6, 17.2), 8.8, 1.2, boxstyle="round,pad=0,rounding_size=0.2",
                                   facecolor=CAJA, edgecolor=TINTA_TENUE))
    panel.text(1.0, 17.8, f"#{pedido} · {len(ubicaciones)} productos   ▾", va="center",
               fontsize=7.5, color=TINTA)
    panel.text(0.6, 16.0, "Técnicas", fontsize=8, fontweight="bold", color=TINTA)
    for i, t in enumerate(TECNICAS):
        yy = 15.0 - i * 1.1
        panel.add_patch(FancyBboxPatch((0.6, yy - 0.3), 0.6, 0.6, boxstyle="round,pad=0,rounding_size=0.1",
                                       facecolor=AZUL, edgecolor=AZUL))
        panel.text(1.6, yy, t, va="center", fontsize=7.5, color=TINTA)
    panel.add_patch(FancyBboxPatch((0.6, 8.2), 8.8, 1.3, boxstyle="round,pad=0,rounding_size=0.3",
                                   facecolor=NARANJA, edgecolor=NARANJA))
    panel.text(5.0, 8.85, "Calcular ruta", ha="center", va="center", fontsize=8.5,
               fontweight="bold", color="#ffffff")
    panel.text(0.6, 7.0, "Orden de visita", fontsize=8, fontweight="bold", color=TINTA)
    for i, u in enumerate(mejor.orden):
        nombre = nodos[u]["producto"]
        nombre = nombre if len(nombre) <= 24 else nombre[:23] + "…"
        panel.text(0.6, 6.1 - i * 0.7, f"{i + 1}. {nombre}", fontsize=6.5, color=TINTA_SECUNDARIA)

    # Almacén con la ruta
    vista = fig.add_axes([0.29, 0.36, 0.69, 0.54])
    dibujar_almacen(vista, lag, nodos, color_pasillo=LINEA_TENUE)
    puntos(vista, nodos, de_tipo(nodos, "estante"), s=0.8, color=LINEA_TENUE, zorder=2)
    vista.plot([nodos[n]["x"] for n in mejor.camino], [nodos[n]["y"] for n in mejor.camino],
               color=COLOR_TECNICA[mejor.tecnica], linewidth=1.6, zorder=4)
    puntos(vista, nodos, mejor.orden, s=22, color=COLOR_TECNICA[mejor.tecnica],
           edgecolors=FONDO, linewidths=0.8, zorder=5)
    vista.set_aspect("equal")
    vista.axis("off")
    vista.set_title(f"Ruta más corta ({mejor.tecnica}): {metros(mejor.distancia)}", fontsize=8)

    # Tabla de resultados
    tabla = fig.add_axes([0.29, 0.06, 0.69, 0.26])
    tabla.axis("off")
    filas = [["Técnica", "Distancia", "Tiempo", "Brecha vs. óptima"]]
    for r in resultados:
        brecha = "—" if not r.calculado else f"+{(r.distancia / optima - 1) * 100:.1f} %".replace(".", ",")
        if r.calculado and r.distancia - optima < 1e-6:
            brecha = "0 % (óptima)"
        filas.append([r.tecnica, metros(r.distancia), milisegundos(r.tiempo_ms), brecha])
    t = tabla.table(cellText=filas, loc="center", cellLoc="left", colWidths=[0.34, 0.2, 0.18, 0.28])
    t.auto_set_font_size(False)
    t.set_fontsize(7.5)
    t.scale(1, 1.1)
    for (fila, _), celda in t.get_celld().items():
        celda.set_edgecolor(LINEA_TENUE)
        if fila == 0:
            celda.set_text_props(fontweight="bold", color=TINTA)
            celda.set_facecolor(GRIS_PANEL)
    guardar(fig, SALIDA, "interfaz.png")


def main() -> None:
    lag, nodos = cargar_grafo()
    pedidos = cargar_pedidos(nodos)
    print("Diagramas:")
    diagrama_arquitectura(lag, nodos)
    diagrama_flujo()
    boceto_interfaz(lag, nodos, pedidos)


if __name__ == "__main__":
    main()
