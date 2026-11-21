"""Evaluación de las técnicas sobre una muestra de pedidos reales.

Para cada tamaño de pedido (2 a 30 productos) toma hasta MUESTRA pedidos al azar
(semilla fija) y registra, por técnica, la distancia, el tiempo y la brecha
frente a la ruta óptima (Held-Karp, solo hasta config.LIMITE_HELD_KARP productos).

Escribe en figuras/resultados/:
    experimentos.csv          una fila por pedido y técnica
    experimentos_resumen.csv  promedios por tamaño de pedido
    experimentos.png          tiempo y brecha según el tamaño

Uso:
    python src/experimentos.py
"""

import random

import matplotlib.pyplot as plt
import pandas as pd

import config
from algoritmos import resolver
from estilo import ANCHO_FIGURA, COLOR_TECNICA, LINEA_TENUE, TINTA_TENUE, guardar, preparar_ejes
from grafo import cargar_grafo, cargar_pedidos

MUESTRA = 30
SEMILLA = 2026
TAMANOS = range(2, 31)
SALIDA = config.FIG_RESULTADOS


def elegir_muestra(pedidos):
    """Hasta MUESTRA pedidos al azar de cada tamaño."""
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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(ANCHO_FIGURA, 3.4))

    for t in ["Held-Karp", "Backtracking", "Vecino más cercano", "Recorrido en S"]:
        datos = resumen[resumen["tecnica"] == t]
        ax1.plot(datos["n"], datos["tiempo_ms"], marker="o", ms=3, lw=1.6, color=COLOR_TECNICA[t], label=t)
    dijkstra = resumen.groupby("n")["dijkstra_ms"].mean()
    ax1.plot(dijkstra.index, dijkstra.values, ls="--", lw=1.4, color=TINTA_TENUE, label="Dijkstra (matriz)")
    ax1.set_yscale("log")
    ax1.set_title("Tiempo promedio según el tamaño del pedido")
    ax1.set_ylabel("milisegundos (escala log)", color=TINTA_TENUE)
    preparar_ejes(ax1, "productos del pedido (n)")

    for t in ["Vecino más cercano", "Recorrido en S", "Orden del carrito"]:
        datos = resumen[(resumen["tecnica"] == t) & resumen["brecha_pct"].notna()]
        ax2.plot(datos["n"], datos["brecha_pct"], marker="o", ms=3, lw=1.6, color=COLOR_TECNICA[t], label=t)
    ax2.set_title("Distancia extra frente a la ruta óptima")
    ax2.set_ylabel("% sobre Held-Karp", color=TINTA_TENUE)
    preparar_ejes(ax2, f"productos del pedido (n ≤ {config.LIMITE_HELD_KARP})")

    for ax in (ax1, ax2):
        ax.grid(axis="y", color=LINEA_TENUE, lw=0.6)
        ax.legend(frameon=False, fontsize=7)
    fig.tight_layout()
    guardar(fig, SALIDA, "experimentos.png")


def main():
    lag, nodos = cargar_grafo()
    pedidos = cargar_pedidos(nodos)
    muestra = elegir_muestra(pedidos)
    print(f"Muestra: {len(muestra)} pedidos de {TAMANOS.start} a {TAMANOS.stop - 1} productos")

    datos = ejecutar(lag, nodos, pedidos, muestra)
    SALIDA.mkdir(parents=True, exist_ok=True)
    datos.to_csv(SALIDA / "experimentos.csv", index=False)
    resumen = (datos.groupby(["n", "tecnica"])
               .agg(pedidos=("order_id", "size"), distancia_m=("distancia_m", "mean"),
                    tiempo_ms=("tiempo_ms", "mean"), dijkstra_ms=("dijkstra_ms", "mean"),
                    brecha_pct=("brecha_pct", "mean"))
               .round(3).reset_index())
    resumen.to_csv(SALIDA / "experimentos_resumen.csv", index=False)
    figura(resumen)

    # Resumen
    con_optima = datos[datos["brecha_pct"].notna()]
    hk = con_optima[con_optima["tecnica"] == "Held-Karp"].set_index("order_id")["distancia_m"]
    bt = con_optima[con_optima["tecnica"] == "Backtracking"].set_index("order_id")["distancia_m"]
    iguales = (hk.loc[bt.index] - bt).abs().lt(0.01).sum()
    print(f"\nHeld-Karp y backtracking coinciden en {iguales} de {len(bt)} pedidos "
          f"(n ≤ {config.LIMITE_BACKTRACKING})")
    for t in ["Vecino más cercano", "Recorrido en S", "Orden del carrito"]:
        b = con_optima[con_optima["tecnica"] == t]["brecha_pct"]
        print(f"{t:<20} brecha promedio {b.mean():5.1f} %   óptima en {b.lt(0.01).mean():.0%} de los pedidos")
    carrito = con_optima[con_optima["tecnica"] == "Orden del carrito"]["brecha_pct"].mean()
    print(f"La ruta óptima ahorra en promedio {1 - 1 / (1 + carrito / 100):.0%} frente al orden del carrito")
    tiempos = datos[datos["tecnica"] == "Held-Karp"].groupby("n")["tiempo_ms"].max()
    print(f"Held-Karp, peor tiempo con n = {config.LIMITE_HELD_KARP}: "
          f"{tiempos.get(config.LIMITE_HELD_KARP, float('nan')):.0f} ms")


if __name__ == "__main__":
    main()
