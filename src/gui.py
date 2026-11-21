"""Interfaz gráfica de SmartPick (Tkinter + Matplotlib).

Pestañas:
- Rutas: elegir un pedido real, calcular su ruta con cada técnica, verla
  dibujada sobre el almacén y comparar distancia, tiempo y brecha frente a la
  ruta óptima.
- Grafo y dataset, Resultados: figuras del almacén y de la comparación de
  técnicas, que generan visualizar.py y experimentos.py.

Uso:
    python src/gui.py
"""

import random
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

import config
from algoritmos import TECNICAS, distancia_optima, resolver
from estilo import (COLOR_TECNICA, FONDO, LINEA_TENUE, SERIES, TINTA, TINTA_SECUNDARIA,
                    de_tipo, dibujar_almacen, etiquetar_zonas, metros, milisegundos,
                    preparar_ejes, puntos)
from grafo import cargar_grafo, cargar_pedidos


# Pestañas de figuras
VIS, RES = config.FIG_VISUALIZACION, config.FIG_RESULTADOS
GALERIAS = [
    ("Grafo y dataset", "visualizar.py", [
        ("Grafo completo del almacén", VIS / "grafo_completo.png"),
        *[(f"Subgrafo zona {z} · {d['nombre']}", VIS / f"subgrafo_zona_{z}.png")
          for z, d in config.ZONAS.items()],
        ("Pedido de ejemplo", VIS / "pedido_ejemplo.png"),
        ("Mapa de demanda", VIS / "mapa_demanda.png"),
        ("Tamaño de los pedidos", VIS / "tamano_pedidos.png"),
    ]),
    ("Resultados", "experimentos.py", [
        ("Tiempo y distancia extra de cada técnica", RES / "experimentos.png"),
    ]),
]


class Galeria(ttk.Frame):
    """Pestaña que muestra figuras PNG."""

    def __init__(self, contenedor, figuras, script):
        super().__init__(contenedor, padding=14)
        self.figuras = dict(figuras)
        self.script = script
        self.cargadas = {}
        self.imagen = None

        fila = ttk.Frame(self)
        fila.pack(fill="x")
        self.var = tk.StringVar(value=figuras[0][0])
        lista = ttk.Combobox(fila, textvariable=self.var, values=list(self.figuras),
                             state="readonly", width=45)
        lista.pack(side="left")
        lista.bind("<<ComboboxSelected>>", lambda _: self.mostrar())
        ttk.Label(fila, text=f"Se regeneran con: python src/{script}",
                  foreground=TINTA_SECUNDARIA).pack(side="left", padx=12)

        self.vista = tk.Label(self, background=FONDO, foreground=TINTA_SECUNDARIA)
        self.vista.pack(fill="both", expand=True, pady=(10, 0))
        self.vista.bind("<Configure>", lambda _: self.mostrar())

    def mostrar(self):
        """Muestra la figura elegida ajustada a la pestaña."""
        archivo = self.figuras[self.var.get()]
        if not archivo.exists():
            self.imagen = None
            self.vista.config(image="", text=f"Falta {archivo.name}. "
                                             f"Genérala con: python src/{self.script}")
            return
        if archivo not in self.cargadas:
            self.cargadas[archivo] = tk.PhotoImage(file=str(archivo))
        original = self.cargadas[archivo]
        ancho, alto = max(self.vista.winfo_width(), 1), max(self.vista.winfo_height(), 1)
        factor = max(1, -(-original.width() // ancho), -(-original.height() // alto))
        self.imagen = original.subsample(factor)
        self.vista.config(image=self.imagen, text="")


class SmartPick(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SmartPick: rutas de picking en el almacén")
        self.geometry("1280x780")
        self.minsize(1050, 650)
        self.configure(bg=FONDO)

        self.lag, self.nodos = cargar_grafo()
        self.pos = {n: (d["x"], d["y"]) for n, d in self.nodos.items()}
        self.pedidos = cargar_pedidos(self.nodos)
        self.ids = sorted(self.pedidos)
        self.resultados = []
        self.artistas = []

        self._estilos()
        pestanas = ttk.Notebook(self)
        pestanas.pack(fill="both", expand=True)
        rutas = ttk.Frame(pestanas)
        pestanas.add(rutas, text="  Rutas  ")
        self._panel_izquierdo(rutas)
        self._panel_derecho(rutas)
        self._dibujar_almacen()
        for titulo, script, figuras in GALERIAS:
            pestanas.add(Galeria(pestanas, figuras, script), text=f"  {titulo}  ")

        self.var_pedido.set(self._etiqueta(config.PEDIDO_EJEMPLO))
        self.calcular()

    def _estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(".", background=FONDO, font=("Segoe UI", 10))
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 11, "bold"))
        estilo.configure("Seccion.TLabel", font=("Segoe UI", 9, "bold"), foreground=TINTA_SECUNDARIA)
        estilo.configure("Accion.TButton", font=("Segoe UI", 10, "bold"),
                         background=SERIES[1], foreground="white", padding=8)
        estilo.map("Accion.TButton", background=[("active", "#d55a2a")])
        estilo.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        estilo.configure("TNotebook", background=FONDO)
        estilo.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(10, 4))

    def _etiqueta(self, pedido: int) -> str:
        return f"#{pedido} · {len(self.pedidos[pedido])} productos"

    def _panel_izquierdo(self, contenedor):
        panel = ttk.Frame(contenedor, padding=14)
        panel.pack(side="left", fill="y")

        ttk.Label(panel, text="SmartPick", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(panel, text=f"{len(self.ids):,} pedidos reales de Instacart".replace(",", " "),
                  foreground=TINTA_SECUNDARIA).pack(anchor="w", pady=(0, 12))

        ttk.Label(panel, text="PEDIDO", style="Seccion.TLabel").pack(anchor="w")
        fila = ttk.Frame(panel)
        fila.pack(fill="x", pady=(2, 4))
        self.var_pedido = tk.StringVar()
        self.combo = ttk.Combobox(fila, textvariable=self.var_pedido, width=24,
                                  values=[self._etiqueta(i) for i in self.ids])
        self.combo.pack(side="left")
        self.combo.bind("<<ComboboxSelected>>", lambda _: self.calcular())
        self.combo.bind("<Return>", lambda _: self.calcular())
        ttk.Button(fila, text="Al azar", command=self.al_azar).pack(side="left", padx=(6, 0))
        ttk.Label(panel, text="Escribe el número y presiona Enter.",
                  foreground=TINTA_SECUNDARIA, font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 12))

        ttk.Label(panel, text="TÉCNICAS", style="Seccion.TLabel").pack(anchor="w")
        self.var_tecnicas = {}
        for tecnica in TECNICAS:
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(panel, text=tecnica, variable=var).pack(anchor="w")
            self.var_tecnicas[tecnica] = var

        ttk.Button(panel, text="Calcular ruta", style="Accion.TButton",
                   command=self.calcular).pack(fill="x", pady=14)

        ttk.Label(panel, text="PRODUCTOS DEL PEDIDO", style="Seccion.TLabel").pack(anchor="w")
        ttk.Label(panel, text="en el orden de la ruta seleccionada",
                  foreground=TINTA_SECUNDARIA, font=("Segoe UI", 8)).pack(anchor="w")
        self.lista = tk.Listbox(panel, width=40, height=18, borderwidth=0, highlightthickness=1,
                                highlightcolor=LINEA_TENUE, font=("Segoe UI", 9), activestyle="none")
        self.lista.pack(fill="both", expand=True, pady=(4, 0))

    def _panel_derecho(self, contenedor):
        panel = ttk.Frame(contenedor, padding=(0, 14, 14, 14))
        panel.pack(side="left", fill="both", expand=True)

        self.fig = Figure(figsize=(9, 4), dpi=100, facecolor=FONDO)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.05, right=0.99, top=0.9, bottom=0.16)
        self.canvas = FigureCanvasTkAgg(self.fig, master=panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.estado = ttk.Label(panel, foreground=TINTA_SECUNDARIA)
        self.estado.pack(anchor="w", pady=(6, 4))

        columnas = ("tecnica", "distancia", "tiempo", "brecha", "nota")
        self.tabla = ttk.Treeview(panel, columns=columnas, show="headings", height=5,
                                  selectmode="browse")
        for col, titulo, ancho, lado in [("tecnica", "Técnica", 190, "w"),
                                         ("distancia", "Distancia", 110, "e"),
                                         ("tiempo", "Tiempo", 100, "e"),
                                         ("brecha", "Brecha vs. óptima", 140, "e"),
                                         ("nota", "Nota", 260, "w")]:
            self.tabla.heading(col, text=titulo, anchor=lado)
            self.tabla.column(col, width=ancho, anchor=lado, stretch=col == "nota")
        self.tabla.pack(fill="x")
        self.tabla.bind("<<TreeviewSelect>>", lambda _: self.mostrar_ruta())
        ttk.Label(panel, text="Selecciona una fila para dibujar su ruta. El tiempo es solo el "
                              "cálculo del orden de visita; Dijkstra se mide aparte.",
                  foreground=TINTA_SECUNDARIA, font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))

    def _dibujar_almacen(self):
        """El almacén en tonos neutros; la ruta se dibuja encima."""
        ax = self.ax
        dibujar_almacen(ax, self.lag, self.nodos, color_pasillo=LINEA_TENUE)
        puntos(ax, self.nodos, de_tipo(self.nodos, "estante"), s=1.2, color=LINEA_TENUE, zorder=2)
        etiquetar_zonas(ax, self.nodos)
        ax.set_aspect("equal")
        ax.margins(0.03, 0.12)
        preparar_ejes(ax, etiqueta_x=None)

    def _pedido_elegido(self):
        texto = self.var_pedido.get().strip().lstrip("#").split(" ")[0]
        try:
            pedido = int(texto)
        except ValueError:
            pedido = None
        if pedido not in self.pedidos:
            messagebox.showwarning("SmartPick", f"No existe el pedido «{texto}».")
            return None
        self.var_pedido.set(self._etiqueta(pedido))
        return pedido

    def al_azar(self):
        self.var_pedido.set(self._etiqueta(random.choice(self.ids)))
        self.calcular()

    def calcular(self):
        pedido = self._pedido_elegido()
        if pedido is None:
            return
        tecnicas = [t for t in TECNICAS if self.var_tecnicas[t].get()]
        if not tecnicas:
            messagebox.showinfo("SmartPick", "Elige al menos una técnica.")
            return
        self.pedido = pedido
        self.config(cursor="watch")
        self.update_idletasks()
        self.resultados, t_dijkstra = resolver(self.lag, self.nodos, self.pedidos[pedido], tecnicas)
        self.config(cursor="")

        n = len(self.pedidos[pedido])
        self.estado.config(text=f"Pedido #{pedido}: {n} productos · Dijkstra ({n + 1} ejecuciones) "
                                f"y matriz {n + 1}×{n + 1}: {milisegundos(t_dijkstra)}")
        optima = distancia_optima(self.resultados)
        self.tabla.delete(*self.tabla.get_children())
        for r in self.resultados:
            brecha = "—"
            if r.calculado and optima:
                brecha = f"+{(r.distancia / optima - 1) * 100:.1f} %".replace(".", ",")
                brecha = "0 % (óptima)" if r.distancia - optima < 1e-6 else brecha
            self.tabla.insert("", "end", iid=r.tecnica, values=(
                r.tecnica, metros(r.distancia), milisegundos(r.tiempo_ms), brecha, r.nota))

        calculados = [r for r in self.resultados if r.calculado]
        mejor = min(calculados, key=lambda r: (r.distancia, TECNICAS.index(r.tecnica)))
        self.tabla.selection_set(mejor.tecnica)

    def mostrar_ruta(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            return
        r = next(r for r in self.resultados if r.tecnica == seleccion[0])
        for artista in self.artistas:
            artista.remove()
        self.artistas = []
        self.lista.delete(0, "end")
        if not r.calculado:
            self.ax.set_title(f"{r.tecnica}: no se calcula ({r.nota})", loc="left", fontsize=10)
            self.canvas.draw_idle()
            return

        color = COLOR_TECNICA[r.tecnica]
        xs = [self.pos[n][0] for n in r.camino]
        ys = [self.pos[n][1] for n in r.camino]
        self.artistas += self.ax.plot(xs, ys, color=color, lw=1.8, alpha=0.9, zorder=3)
        px = [self.pos[u][0] for u in r.orden]
        py = [self.pos[u][1] for u in r.orden]
        self.artistas.append(self.ax.scatter(px, py, s=60, color=color, edgecolors=FONDO,
                                             linewidths=1, zorder=4))
        for i, (x, y) in enumerate(zip(px, py), start=1):
            self.artistas.append(self.ax.annotate(str(i), (x, y), xytext=(0, 6),
                                                  textcoords="offset points", ha="center",
                                                  fontsize=7.5, fontweight="bold", color=TINTA,
                                                  zorder=5))
        self.ax.set_title(f"{r.tecnica}: {metros(r.distancia)} · pedido #{self.pedido}",
                          loc="left", fontsize=10, fontweight="bold")
        leyenda = self.ax.legend(handles=[
            Line2D([], [], color=color, lw=2, label="Ruta"),
            Line2D([], [], ls="", marker="o", ms=7, color=color, label="Producto (orden de visita)"),
            Line2D([], [], ls="", marker="s", ms=7, color=TINTA, label="Depósito")],
            loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=False, fontsize=8)
        self.artistas.append(leyenda)
        self.canvas.draw_idle()

        for i, u in enumerate(r.orden, start=1):
            self.lista.insert("end", f"{i:>2}. {u}  {self.nodos[u].get('producto', '')}")


if __name__ == "__main__":
    SmartPick().mainloop()
