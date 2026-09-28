# SmartPick: contexto del proyecto

**Curso:** 1ACC0184 Complejidad Algorítmica, 2026-20
**Grupo 2, Caso de estudio 2:** Gestión de almacenes inteligentes (referencia: Amazon)

| Integrante | Código |
| --- | --- |
| Palma de los Santos, Elynor Mikela | U20241A972 |
| Flores Pinchi, José Fernando | U20241A290 |
| Julca Cruz, Renso Anthony | U202121579 |

## 1. De qué trata el proyecto

En un almacén, el **picking** es recorrer los pasillos para recoger los productos de
un pedido. Es la operación más costosa del almacén, y la mayor parte de ese tiempo se
va en caminar entre estantes. Nuestro objetivo:

1. **Modelar el almacén como un grafo**: estantes e intersecciones son nodos; los
   tramos de pasillo son aristas con su distancia.
2. **Ubicar los productos** en ese almacén a partir de datos reales.
3. **Calcular la ruta más corta** para recoger los productos de cada pedido, con las
   técnicas del curso.

## 2. Entregas y fechas

| Hito | Fecha límite | Qué se entrega | Puntaje |
| --- | --- | --- | --- |
| **TB1** | **dom 04/10/2026 23:59** | Informe: problema, dataset, visualización del grafo, propuesta preliminar | 0 a 20 |
| Hito 2 | dom 22/11/2026 23:59 | Informe y diseño del aplicativo | 0 a 5 |
| **TB2** | dom 29/11/2026 23:59 | .zip con código, dataset, link del video (12 min, 4 por persona) e informe .docx | 0 a 15 |
| Exposición | Semana 7 (TB1) y semana 15 (TB2) | 10 min, vestimenta formal, máximo 15 diapositivas | |

**Requisitos del TB1:**

- Informe de 4 a 10 páginas, con la plantilla oficial .docx.
- Grafo de **al menos 1500 nodos**, con un mínimo de 500 por integrante.
- **Mostrar el grafo completo y/o subgrafos.**
- Archivo: `TB1_1ACC0184_2026-20_<Códigos>_<Apellidos>`.

## 3. Rúbrica del TB1

| Criterio | Pts | Qué se necesita para la nota máxima |
| --- | --- | --- |
| Formato | 4 | Seguir la estructura de la plantilla sin errores |
| Problema | 5 | Problema real con **datos reales**, contexto y **objetivos completos** |
| Dataset | 5 | Describir la estructura del dataset **y su origen** |
| Propuesta | 6 | Técnica elegida, **por qué** y **respaldo bibliográfico** |

## 4. Cómo trabajamos

| Qué | Dónde |
| --- | --- |
| Informe | **Google Docs**, sobre la plantilla UPC; al final se exporta a .docx |
| Código, datos y figuras | **Este repositorio**, en Python |
| Declaración de uso de IA | Anexos del informe y exposición (lo exige el enunciado) |

Las reglas están en [CONTRIBUTING.md](../CONTRIBUTING.md).

## 5. El dataset: Instacart Market Basket

Datos reales y anonimizados de compras de supermercado en línea, publicados por
Instacart en 2017 y disponibles en Kaggle. No existen layouts públicos de almacenes
reales, pero sí productos y pedidos reales: los pedidos de Instacart son listas de
picking reales.

| Archivo | Contenido | Filas |
| --- | --- | --- |
| `products.csv` | producto, pasillo y departamento | 49 688 |
| `aisles.csv` | nombre de cada pasillo | 134 |
| `departments.csv` | nombre de cada departamento | 21 |
| `orders.csv` | un pedido por fila (206 209 usuarios) | 3 421 083 |
| `order_products__train.csv` | productos de cada pedido de entrenamiento | 1 384 617 |
| `order_products__prior.csv` | productos de los pedidos anteriores | ~32 millones |

Se excluyen los departamentos `missing` y `other`, que no clasifican sus productos.
Los originales no se suben (ver [data/raw/README.md](../data/raw/README.md)); en el
repositorio está la versión reducida:

| Archivo | Contenido |
| --- | --- |
| `data/processed/productos.csv` | los 1 500 productos del almacén y su ubicación |
| `data/processed/pedidos.csv` | 8 771 pedidos reales con todos sus productos en el almacén |
| `data/processed/nodos.csv` | los 2 311 nodos del grafo |
| `data/processed/aristas.csv` | las 2 339 aristas, con su distancia en metros |

Los 1 500 productos elegidos (los 500 más pedidos de cada zona) cubren el **56,2 %**
de todas las líneas de pedido del conjunto de entrenamiento. Los pedidos tienen en
promedio 4,4 productos (mediana 3, máximo 30).

## 6. Modelo del almacén

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

**Nodos (2 311):**

| Tipo | Por zona | Total | Qué es |
| --- | --- | --- | --- |
| Estante | 500 | 1 500 | Ubicación de un producto |
| Punto de pasillo | 250 | 750 | Por donde camina el picker |
| Intersección | 20 | 60 | Extremos de cada pasillo |
| Depósito | | 1 | Inicio y fin de cada ruta |

Cada zona tiene **770 nodos**, por encima de los 500 por integrante que pide el curso.

**Aristas (2 339):** no dirigidas, con peso en metros. Unen puntos consecutivos de un
pasillo (1,2 m), cada estante con su punto de pasillo (1,5 m), intersecciones
vecinas por los pasillos transversales (5 m) y el depósito con el pasillo central
(5 m). El grafo es conexo, con grado promedio 2,02.

**Ubicación de productos:** dentro de cada zona, los productos se ordenan por
departamento y pasillo de Instacart y se llenan los estantes en orden, así los de la
misma familia quedan juntos. Optimizar esta ubicación es parte del caso y queda como
trabajo posterior.

## 7. Técnicas (propuesta preliminar)

| Técnica | Para qué |
| --- | --- |
| **Grafos + BFS** | Modelar el almacén y calcular distancias entre los puntos de un pedido |
| **Programación dinámica (Held-Karp)** | Ruta óptima para pedidos pequeños (unos 15 productos o menos) |
| **Voraz (vecino más cercano)** | Ruta rápida para pedidos grandes |
| **Backtracking con poda** | Comparar resultados contra la solución óptima |
| **Divide y vencerás** | Resolver por zonas y luego combinar |
| **UFDS** | Verificar la conectividad del almacén y agrupar productos que se piden juntos |

## 8. Figuras para el informe

Están en `figuras/` y se regeneran con `python src/visualizar.py`.

| Archivo | Sección del informe |
| --- | --- |
| `grafo_completo.png` | 3. Visualización: grafo completo, por zona |
| `subgrafo_zona_A.png`, `_B`, `_C` | 3. Visualización: un subgrafo por integrante |
| `pedido_ejemplo.png` y `.csv` | 4. Propuesta: un pedido real sobre el almacén |
| `estadisticas.csv` | 2. Dataset: nodos y aristas por zona |

## 9. Próximos pasos

1. [x] Descargar el dataset de Kaggle.
2. [x] Construir el grafo y las visualizaciones.
3. [x] Asignar una zona a cada integrante (ver el reparto en [CONTRIBUTING.md](../CONTRIBUTING.md)).
4. [ ] Redactar el informe en Google Docs y pegar las figuras.
5. [ ] Escribir la declaración de uso de IA.
6. [ ] Exportar a .docx, revisar formato y páginas, y entregar antes del **domingo 04/10**.
