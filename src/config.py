"""Parámetros del almacén, de los algoritmos y rutas del proyecto."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATA_RAW = RAIZ / "data" / "raw"
DATA_PROCESSED = RAIZ / "data" / "processed"

FIGURAS = RAIZ / "figuras"
FIG_VISUALIZACION = FIGURAS / "visualizacion"
FIG_DISENO = FIGURAS / "diseno"
FIG_RESULTADOS = FIGURAS / "resultados"

# Almacén en metros
PASILLOS_POR_ZONA = 10
POSICIONES_POR_PASILLO = 25
LARGO_POSICION = 1.2
ANCHO_PASILLO = 3.0
PROFUNDIDAD_ESTANTE = 1.0
DISTANCIA_DEPOSITO = 5.0

# Distancia entre los centros de dos pasillos vecinos
SEPARACION_PASILLOS = ANCHO_PASILLO + 2 * PROFUNDIDAD_ESTANTE
# Departamentos de Instacart de cada zona (sin "missing" ni "other")

ZONAS = {
    "A": {
        "nombre": "Frescos",
        "responsable": "Palma",
        "departamentos": ["produce", "dairy eggs", "meat seafood", "deli", "bakery", "frozen"],
    },
    "B": {
        "nombre": "Despensa",
        "responsable": "Flores",
        "departamentos": ["pantry", "dry goods pasta", "canned goods", "breakfast",
                          "snacks", "international", "bulk"],
    },
    "C": {
        "nombre": "Bebidas y hogar",
        "responsable": "Julca",
        "departamentos": ["beverages", "alcohol", "household", "personal care",
                          "babies", "pets"],
    },
}

# Nombres en español para las figuras
DEPARTAMENTOS_ES = {
    "produce": "Frutas y verduras",
    "dairy eggs": "Lácteos y huevos",
    "meat seafood": "Carnes y pescados",
    "deli": "Charcutería",
    "bakery": "Panadería",
    "frozen": "Congelados",
    "pantry": "Despensa",
    "dry goods pasta": "Pastas y secos",
    "canned goods": "Enlatados",
    "breakfast": "Desayuno",
    "snacks": "Snacks",
    "international": "Internacional",
    "bulk": "A granel",
    "beverages": "Bebidas",
    "alcohol": "Bebidas alcohólicas",
    "household": "Hogar",
    "personal care": "Cuidado personal",
    "babies": "Bebés",
    "pets": "Mascotas",
}

# Un producto por estante
UBICACIONES_POR_ZONA = PASILLOS_POR_ZONA * POSICIONES_POR_PASILLO * 2
# Tamaño máximo de pedido para las técnicas exactas

LIMITE_HELD_KARP = 15
LIMITE_BACKTRACKING = 10

# Pedido de ejemplo del informe (8 productos en las tres zonas)
PEDIDO_EJEMPLO = 1682
