"""Parámetros del almacén y rutas del proyecto.

Todo lo que se puede ajustar del modelo vive aquí, para que los demás
scripts no tengan números sueltos.
"""

from pathlib import Path

# --- Rutas -------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent.parent
DATA_RAW = RAIZ / "data" / "raw"              # CSV originales de Instacart (no se suben)
DATA_PROCESSED = RAIZ / "data" / "processed"  # versión reducida (sí se sube)
FIGURAS = RAIZ / "figuras"                    # imágenes para el informe

# --- Geometría del almacén (en metros) -----------------------------------------
#
# Layout clásico de picking manual: pasillos paralelos con un pasillo
# transversal al frente y otro al fondo. El picker camina por el centro del
# pasillo y toma los productos de los estantes a su izquierda y derecha.

PASILLOS_POR_ZONA = 10
POSICIONES_POR_PASILLO = 25   # posiciones de estante a lo largo de cada pasillo
LARGO_POSICION = 1.2          # ancho de un módulo de estantería
ANCHO_PASILLO = 3.0           # espacio por donde camina el picker
PROFUNDIDAD_ESTANTE = 1.0     # cada pasillo tiene estantes a ambos lados
DISTANCIA_DEPOSITO = 5.0      # del depósito al pasillo transversal del frente

# Distancia entre el centro de un pasillo y el del siguiente:
# medio pasillo + estante + estante + medio pasillo.
SEPARACION_PASILLOS = ANCHO_PASILLO + 2 * PROFUNDIDAD_ESTANTE

# --- Zonas -------------------------------------------------------------------
#
# Cada zona agrupa departamentos de Instacart y ocupa PASILLOS_POR_ZONA
# pasillos contiguos. Se excluyen "missing" y "other" porque no clasifican
# sus productos.

ZONAS = {
    "A": {
        "nombre": "Frescos",
        "departamentos": ["produce", "dairy eggs", "meat seafood", "deli", "bakery", "frozen"],
    },
    "B": {
        "nombre": "Despensa",
        "departamentos": ["pantry", "dry goods pasta", "canned goods", "breakfast",
                          "snacks", "international", "bulk"],
    },
    "C": {
        "nombre": "Bebidas y hogar",
        "departamentos": ["beverages", "alcohol", "household", "personal care",
                          "babies", "pets"],
    },
}

# Nombres en español para las figuras y tablas.
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

# Cada ubicación de estante guarda un producto: los N más pedidos de cada zona.
UBICACIONES_POR_ZONA = PASILLOS_POR_ZONA * POSICIONES_POR_PASILLO * 2
