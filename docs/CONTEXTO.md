# SmartPick: contexto del proyecto

**Curso:** 1ACC0184 Complejidad Algorítmica, 2026-20
**Grupo 2, Caso de estudio 2:** Gestión de almacenes inteligentes (referencia: Amazon).
Objetivo del caso: ubicar productos y optimizar el picking.

| Integrante | Código |
| --- | --- |
| Palma de los Santos, Elynor Mikela | U20241A972 |
| Flores Pinchi, José Fernando | U20241A290 |
| Julca Cruz, Renso Anthony | U202121579 |

## 1. De qué trata el proyecto

En un almacén, el **picking** es recorrer los pasillos para recoger los productos de
un pedido. Es la operación más costosa del almacén, y la mayor parte de ese tiempo se
va en caminar entre estantes. Nuestro objetivo:

1. **Modelar el almacén como un grafo**: estantes, puntos de pasillo e intersecciones
   son nodos; los tramos de pasillo son aristas con su distancia en metros.
2. **Ubicar los productos** en ese almacén a partir de datos reales.
3. **Calcular la ruta más corta** para recoger los productos de cada pedido, con las
   técnicas del curso, y comparar su calidad y su tiempo.

## 2. Entregas

| Hito | Fecha límite | Qué se entrega | Puntaje |
| --- | --- | --- | --- |
| TB1 | dom 04/10/2026 23:59 | Informe: problema, dataset, visualización del grafo, propuesta preliminar | 0 a 20 |
| **Hito 2** | **dom 22/11/2026 23:59** | Informe con problema, dataset, propuesta y **diseño del aplicativo** | 0 a 5 |
| TB2 | dom 29/11/2026 23:59 | .zip con código, dataset, link del video (12 min, 4 por persona) e informe .docx | 0 a 15 |
| Exposición | Semana 15 | 10 min, vestimenta formal, máximo 15 diapositivas | |

**Hito 2 (segundo hito).** Informe con estas secciones, evaluado con la *Rúbrica de
Trabajo Final*:

| Sección | Qué pide | Material en el repositorio |
| --- | --- | --- |
| Descripción del problema | Descripción y fundamentación, **citando fuentes** | sección 1 de este documento (las fuentes se agregan en el informe) |
| Descripción del dataset | Características y **origen** de los datos | sección 3, `figuras/visualizacion/` |
| Propuesta | Objetivo, técnica y metodología **finalmente** usadas | secciones 5 y 6, `figuras/resultados/` |
| Diseño del aplicativo | Procesos del diseño (ingeniería de software o análisis de algoritmos) | `figuras/diseno/`, sección 5 |

Archivo: `TrabajoFinal_1ACC0184_2026-20_<CódigoAlum>_<ApellidoAlum>`, con el código y
el primer apellido de cada integrante.

## 3. El dataset: Instacart Market Basket

Datos reales y anonimizados de compras de supermercado en línea, publicados por
Instacart en 2017 y disponibles en Kaggle. No existen layouts públicos de almacenes
reales, pero sí productos y pedidos reales: los pedidos de Instacart son listas de
picking reales.

| Archivo original | Contenido | Filas |
| --- | --- | --- |
| `products.csv` | producto, pasillo y departamento | 49 688 |
| `aisles.csv` | nombre de cada pasillo | 134 |
| `departments.csv` | nombre de cada departamento | 21 |
| `orders.csv` | un pedido por fila (206 209 usuarios) | 3 421 083 |
| `order_products__train.csv` | productos de cada pedido de entrenamiento | 1 384 617 |
| `order_products__prior.csv` | productos de los pedidos anteriores (no se usa) | ~32 millones |

Se excluyen los departamentos `missing` y `other`, que no clasifican sus productos.
En el repositorio está la versión reducida que genera `src/dataset.py`:

| Archivo | Contenido |
| --- | --- |
| `data/processed/productos.csv` | los 1 500 productos del almacén y su ubicación |
| `data/processed/pedidos.csv` | 8 771 pedidos reales con todos sus productos en el almacén |
| `data/processed/nodos.csv` | los 2 311 nodos del grafo |
| `data/processed/aristas.csv` | las 2 339 aristas, con su distancia en metros |

Los 1 500 productos elegidos (los 500 más pedidos de cada zona) cubren el **56,2 %**
de las líneas de pedido del conjunto de entrenamiento. Los pedidos tienen en promedio
4,4 productos (mediana 3, máximo 30); el 99,4 % tiene 15 productos o menos.

## 4. Modelo del almacén

Layout clásico de picking manual: pasillos paralelos con un pasillo transversal al
frente y otro al fondo. Los parámetros están en `src/config.py`.

| Parámetro | Valor |
| --- | --- |
| Zonas | 3, contiguas |
| Pasillos por zona | 10 |
| Posiciones por pasillo | 25, con estante a la izquierda y a la derecha |
| Largo de una posición | 1,2 m |
| Ancho de pasillo | 3,0 m |
| Separación entre pasillos | 5,0 m (pasillo + dos estantes de 1 m) |
| Depósito | 5 m frente al pasillo central |

| Zona | Nombre | Departamentos |
| --- | --- | --- |
| A | Frescos | frutas y verduras, lácteos y huevos, carnes y pescados, charcutería, panadería, congelados |
| B | Despensa | despensa, pastas y secos, enlatados, desayuno, snacks, internacional, a granel |
| C | Bebidas y hogar | bebidas, bebidas alcohólicas, hogar, cuidado personal, bebés, mascotas |

| Tipo de nodo | Por zona | Total | Qué es |
| --- | --- | --- | --- |
| Estante | 500 | 1 500 | Ubicación de un producto |
| Punto de pasillo | 250 | 750 | Por donde camina el picker |
| Intersección | 20 | 60 | Extremos de cada pasillo |
| Depósito | | 1 | Inicio y fin de cada ruta |

Cada zona tiene **770 nodos y 778 aristas**, por encima de los 500 nodos por integrante
que pide el curso. Las aristas son no dirigidas y unen puntos consecutivos de un
pasillo (1,2 m), cada estante con su punto de pasillo (1,5 m), intersecciones vecinas
(5 m) y el depósito con el pasillo central (5 m). El grafo se guarda como **lista de
adyacencia**; tiene grado promedio 2,02 y BFS confirma que es conexo.

**Ubicación de productos:** dentro de cada zona, los productos se ordenan por
departamento y pasillo de Instacart y se llenan los estantes en orden, así los de la
misma familia quedan juntos.

## 5. Técnicas: propuesta final

Para un pedido de n productos, la aplicación:

1. Corre **Dijkstra** desde el depósito y desde cada producto y arma una matriz de
   distancias (n + 1) × (n + 1). Así el problema pasa de 2 311 nodos a n + 1 puntos.
2. Decide el **orden de visita** (un problema del viajante sobre esa matriz):

| Técnica | Tipo | Complejidad | Para qué |
| --- | --- | --- | --- |
| Dijkstra | Voraz (BFS con pesos) | O((V + E) log V) por ejecución | Distancia y camino entre dos puntos del almacén |
| Held-Karp | Programación dinámica | O(n² · 2ⁿ) | Ruta óptima, hasta 15 productos |
| Backtracking con poda | Backtracking | O(n!) peor caso | Ruta óptima, hasta 10 productos; valida a Held-Karp |
| Vecino más cercano | Voraz | O(n²) | Ruta rápida para cualquier tamaño |
| BFS | Grafos | O(V + E) | Verificar que el almacén es conexo |
| Recorrido en "S" | Referencia | O(n log n) | Método clásico de los almacenes, para comparar |
| Orden del carrito | Referencia | O(n) | Lo que haría un picker sin optimizar |

**Por qué Dijkstra y no BFS para las distancias:** las aristas tienen pesos distintos
(1,2 m, 1,5 m y 5 m). BFS encuentra el camino con menos aristas, que no siempre es el
más corto en metros; Dijkstra es la extensión voraz de BFS para grafos con pesos.

**Técnicas sugeridas en el caso que no se usan**, y por qué:

| Técnica sugerida | Motivo |
| --- | --- |
| Fuerza bruta | Held-Karp y backtracking dan el mismo óptimo mucho más rápido |
| Divide y vencerás, UFDS, topológico, SCC, MST, flujo máximo | Sirven para la ubicación de productos o para varios pedidos a la vez; quedan como trabajo futuro |
| DP en grafos para múltiples pedidos | Trabajo futuro: el proyecto optimiza un pedido a la vez |

## 6. Resultados (`src/experimentos.py`)

Muestra de 473 pedidos reales (hasta 30 por tamaño, de 2 a 30 productos, semilla fija):

- Held-Karp y backtracking dan la misma distancia en los 270 pedidos de hasta 10
  productos: las dos implementaciones exactas se validan entre sí.
- Frente a la ruta óptima (pedidos de hasta 15 productos):

| Técnica | Distancia extra promedio | Encuentra la óptima |
| --- | --- | --- |
| Vecino más cercano | 3,1 % | 45 % de los pedidos |
| Recorrido en S | 16,1 % | 10 % |
| Orden del carrito | 49,6 % | 13 % |

- La ruta óptima recorre en promedio un **33 % menos** que el orden del carrito.
- Held-Karp tarda unas décimas de segundo con 15 productos; el backtracking ya pasa los
  100 ms con 10. El vecino más cercano tarda menos de 0,1 ms en todos los tamaños. Los
  tiempos dependen de la computadora: se vuelven a medir con `experimentos.py`.

**Limitaciones:**

- Solo se usan pedidos cuyos productos están **todos** entre los 1 500 del almacén, lo
  que favorece los pedidos pequeños.
- Para más de 15 productos hay pocos pedidos en la muestra (entre 1 y 14 por tamaño),
  así que esos promedios son menos confiables.
- El recorrido en S empieza siempre por el primer pasillo de la izquierda y el
  depósito está en el centro; parte de su distancia extra viene de ahí.

## 7. Figuras para el informe

Se regeneran con código; nunca se editan a mano.

| Carpeta | Script | Contenido |
| --- | --- | --- |
| `figuras/visualizacion/` | `visualizar.py` | grafo completo, subgrafo de cada zona, pedido de ejemplo, mapa de demanda, tamaño de pedidos, `estadisticas.csv`, `propiedades.csv` |
| `figuras/diseno/` | `diagramas.py` | arquitectura, diagrama de flujo, boceto de la interfaz |
| `figuras/resultados/` | `experimentos.py` | gráfico de tiempo y brecha, tablas por pedido y resumen |

## 8. Próximos pasos

1. [ ] Hito 2 (dom 22/11): subir el informe al Word online del equipo, revisar
       los cambios de los compañeros y entregar con el nombre pedido.
2. [ ] Declaración de uso de IA en los anexos.
3. [ ] TB2 (dom 29/11): grabar el video (4 min por integrante), armar el .zip con el
       código y el dataset, y preparar la exposición.
