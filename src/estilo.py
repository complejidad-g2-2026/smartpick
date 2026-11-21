"""Colores, formatos y funciones de dibujo comunes a todas las figuras y a la
interfaz (solo matplotlib)."""

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

import config

# Colores
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_TENUE = "#898781"
LINEA_TENUE = "#e1e0d9"
FONDO = "#fcfcfb"

COLOR_ZONA = dict(zip(config.ZONAS, SERIES))
COLOR_TECNICA = {
    "Held-Karp": SERIES[0],
    "Vecino más cercano": SERIES[1],
    "Backtracking": SERIES[6],
    "Recorrido en S": SERIES[3],
    "Orden del carrito": SERIES[7],
}

ANCHO_FIGURA = 8
PPP = 200

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans"],
    "font.size": 8,
    "axes.titlesize": 10,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "figure.facecolor": FONDO,
    "axes.facecolor": FONDO,
    "savefig.facecolor": FONDO,
})


def miles(n: int) -> str:
    """2311 -> '2 311'."""
    return f"{n:,}".replace(",", " ")


def metros(valor) -> str:
    return "—" if valor is None else f"{valor:,.1f}".replace(",", " ").replace(".", ",") + " m"


def milisegundos(valor) -> str:
    if valor is None:
        return "—"
    return (f"{valor:.2f}" if valor < 10 else f"{valor:.0f}").replace(".", ",") + " ms"


def de_tipo(nodos: dict, tipo: str, zona: str | None = None) -> list:
    """Nodos de un tipo, opcionalmente solo de una zona."""
    return [n for n, d in nodos.items()
            if d["tipo"] == tipo and (zona is None or d.get("zona") == zona)]


def puntos(ax, nodos: dict, ids: list, **estilo):
    """Dibuja los nodos `ids` en su posición (x, y)."""
    if not ids:
        return None
    return ax.scatter([nodos[n]["x"] for n in ids], [nodos[n]["y"] for n in ids], **estilo)


def dibujar_almacen(ax, lag: dict, nodos: dict, ids=None, color_pasillo: str = TINTA_TENUE) -> None:
    """Aristas, puntos de pasillo, intersecciones y depósito en tonos neutros.
    Si se pasa `ids`, solo dibuja ese subgrafo."""
    ids = set(nodos) if ids is None else set(ids)
    tramos = [((nodos[u]["x"], nodos[u]["y"]), (nodos[v]["x"], nodos[v]["y"]))
              for u in ids for v in lag[u] if v in ids and u < v]
    ax.add_collection(LineCollection(tramos, colors=LINEA_TENUE, linewidths=0.6, zorder=1))
    visibles = {n: d for n, d in nodos.items() if n in ids}
    puntos(ax, nodos, de_tipo(visibles, "pasillo"), s=1.2, color=color_pasillo, zorder=2)
    puntos(ax, nodos, de_tipo(visibles, "interseccion"), s=6, marker="s",
           color=TINTA_SECUNDARIA, zorder=2)
    puntos(ax, nodos, de_tipo(visibles, "deposito"), s=60, marker="s", color=TINTA, zorder=2)
    ax.autoscale_view()


def etiquetar_zonas(ax, nodos: dict, margen: float = 2.5) -> None:
    """Escribe 'Zona A · Frescos' sobre el centro de cada zona."""
    arriba = max(d["y"] for d in nodos.values()) + margen
    for zona, datos in config.ZONAS.items():
        xs = [nodos[n]["x"] for n in de_tipo(nodos, "estante", zona)]
        ax.text((min(xs) + max(xs)) / 2, arriba, f"Zona {zona} · {datos['nombre']}",
                ha="center", color=TINTA_SECUNDARIA, fontsize=8)


def preparar_ejes(ax, etiqueta_x: str | None = "metros") -> None:
    """Ejes limpios: solo izquierda y abajo, en tonos tenues."""
    if etiqueta_x:
        ax.set_xlabel(etiqueta_x, color=TINTA_TENUE)
    ax.tick_params(colors=TINTA_TENUE, labelsize=7)
    for lado, borde in ax.spines.items():
        borde.set_visible(lado in ("left", "bottom"))
        borde.set_color(LINEA_TENUE)


def guardar(fig, carpeta, nombre: str) -> None:
    """Guarda la figura en carpeta/nombre y la cierra."""
    carpeta.mkdir(parents=True, exist_ok=True)
    fig.savefig(carpeta / nombre, dpi=PPP, bbox_inches="tight")
    plt.close(fig)
    print(f"  {(carpeta / nombre).relative_to(config.RAIZ).as_posix()}")
