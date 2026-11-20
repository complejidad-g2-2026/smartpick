"""Evaluación de las técnicas sobre una muestra de pedidos reales.

Para cada tamaño de pedido (2 a 30 productos) toma hasta MUESTRA pedidos al azar
(semilla fija) y registra, por técnica, la distancia, el tiempo y la brecha
frente a la ruta óptima (Held-Karp, n ≤ 15).

Escribe:
    figuras/experimentos.csv          una fila por pedido y técnica
    figuras/experimentos_resumen.csv  promedios por tamaño de pedido
    figuras/experimentos.png          tiempo y brecha según el tamaño

Uso:
    python src/experimentos.py
"""

import random

import matplotlib.pyplot as plt
import pandas as pd

import config
from algoritmos import TECNICAS, resolver
from almacen import cargar_almacen, cargar_pedidos

MUESTRA = 30
SEMILLA = 2026
TAMANOS = range(2, 31)
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]
TINTA_SECUNDARIA = "#52514e"
TINTA_TENUE = "#898781"
LINEA_TENUE = "#e1e0d9"
COLOR = dict(zip(TECNICAS, [SERIES[0], SERIES[1], SERIES[6], SERIES[3], SERIES[7]]))


def elegir_muestra(pedidos):
    azar = random.Random(SEMILLA)
    elegidos = []
    for n in TAMANOS:
        candidatos = sorted(p for p, u in pedidos.items() if len(u) == n)
        elegidos += azar.sample(candidatos, min(MUESTRA, len(candidatos)))
    return elegidos


def ejecutar(lag, nodos, pedidos, muestra):
    filas = []
    for i, pedido in enumerate(muestra, start=1):
        ubicaciones = pedidos[pedido]
        resultados, t_dijkstra = resolver(lag, nodos, ubicaciones)
        optima = next((r.distancia for r in resultados if r.tecnica == "Held-Karp" and r.calculado), None)
        for r in resultados:
            if not r.calculado:
                continue
            filas.append({"order_id": pedido, "n": len(ubicaciones), "tecnica": r.tecnica,
                          "distancia_m": round(r.distancia, 2),
                          "tiempo_ms": None if r.tiempo_ms is None else round(r.tiempo_ms, 4),
                          "dijkstra_ms": round(t_dijkstra, 2),
                          "brecha_pct": None if optima is None else round((r.distancia / optima - 1) * 100, 3)})
        if i % 100 == 0:
            print(f"  {i}/{len(muestra)} pedidos")
    return pd.DataFrame(filas)


def figura(resumen):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 3.4))

    tecnicas_tiempo = ["Held-Karp", "Backtracking", "Vecino más cercano", "Recorrido en S"]
    for t in tecnicas_tiempo:
        datos = resumen[resumen["tecnica"] == t]
        ax1.plot(datos["n"], datos["tiempo_ms"], marker="o", ms=3, lw=1.6, color=COLOR[t], label=t)
    dijkstra = resumen.groupby("n")["dijkstra_ms"].mean()
    ax1.plot(dijkstra.index, dijkstra.values, ls="--", lw=1.4, color=TINTA_TENUE,
             label="Dijkstra (matriz)")
    ax1.set_yscale("log")
    ax1.set_title("Tiempo promedio según el tamaño del pedido", fontsize=10, loc="left")
    ax1.set_xlabel("productos del pedido (n)")
    ax1.set_ylabel("milisegundos (escala log)")

    for t in ["Vecino más cercano", "Recorrido en S", "Orden del carrito"]:
        datos = resumen[(resumen["tecnica"] == t) & resumen["brecha_pct"].notna()]
        ax2.plot(datos["n"], datos["brecha_pct"], marker="o", ms=3, lw=1.6, color=COLOR[t], label=t)
    ax2.set_title("Distancia extra frente a la ruta óptima", fontsize=10, loc="left")
    ax2.set_xlabel("productos del pedido (n ≤ 15)")
    ax2.set_ylabel("% sobre Held-Karp")

    for ax in (ax1, ax2):
        ax.grid(axis="y", color=LINEA_TENUE, lw=0.6)
        ax.tick_params(colors=TINTA_SECUNDARIA, labelsize=7)
        for lado, spine in ax.spines.items():
            spine.set_visible(lado in ("left", "bottom"))
            spine.set_color(LINEA_TENUE)
        ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(config.FIGURAS / "experimentos.png", dpi=200, facecolor="#fcfcfb")
    plt.close(fig)
    print("  figuras/experimentos.png")


def main():
    lag, nodos = cargar_almacen()
    pedidos = cargar_pedidos(nodos)
    muestra = elegir_muestra(pedidos)
    print(f"Muestra: {len(muestra)} pedidos de {TAMANOS.start} a {TAMANOS.stop - 1} productos")

    datos = ejecutar(lag, nodos, pedidos, muestra)
    datos.to_csv(config.FIGURAS / "experimentos.csv", index=False)
    resumen = (datos.groupby(["n", "tecnica"])
               .agg(pedidos=("order_id", "size"), distancia_m=("distancia_m", "mean"),
                    tiempo_ms=("tiempo_ms", "mean"), dijkstra_ms=("dijkstra_ms", "mean"),
                    brecha_pct=("brecha_pct", "mean"))
               .round(3).reset_index())
    resumen.to_csv(config.FIGURAS / "experimentos_resumen.csv", index=False)
    figura(resumen)

    # Resumen de los pedidos con ruta óptima (n ≤ 15)
    con_optima = datos[datos["brecha_pct"].notna()]
    hk = con_optima[con_optima["tecnica"] == "Held-Karp"].set_index("order_id")["distancia_m"]
    bt = con_optima[con_optima["tecnica"] == "Backtracking"].set_index("order_id")["distancia_m"]
    iguales = (hk.loc[bt.index] - bt).abs().lt(0.01).sum()
    print(f"\nHeld-Karp y backtracking coinciden en {iguales} de {len(bt)} pedidos (n ≤ 10)")
    por_tecnica = con_optima.groupby("tecnica")["brecha_pct"]
    for t in ["Vecino más cercano", "Recorrido en S", "Orden del carrito"]:
        b = con_optima[con_optima["tecnica"] == t]["brecha_pct"]
        print(f"{t:<20} brecha promedio {b.mean():5.1f} %   óptima en {b.lt(0.01).mean():.0%} de los pedidos")
    ahorro = 1 - 1 / (1 + por_tecnica.mean()["Orden del carrito"] / 100)
    print(f"La ruta óptima ahorra en promedio {ahorro:.0%} frente al orden del carrito")
    tiempos = datos[datos["tecnica"] == "Held-Karp"].groupby("n")["tiempo_ms"].max()
    print(f"Held-Karp, peor tiempo con n = 15: {tiempos.get(15, float('nan')):.0f} ms")


if __name__ == "__main__":
    main()
