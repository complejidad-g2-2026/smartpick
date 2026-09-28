"""Genera la versión reducida del dataset de Instacart.

Lee los CSV originales (data/raw/ o la carpeta que se indique con --raw) y
escribe en data/processed/:

- productos.csv: los productos que se guardan en el almacén, con su ubicación.
- pedidos.csv:   pedidos reales cuyos productos están todos en el almacén.

Uso:
    python src/dataset.py --raw C:/ruta/a/instacart
"""

import argparse
from pathlib import Path

import pandas as pd

import config


def cargar_catalogo(raw: Path) -> pd.DataFrame:
    """Productos con el nombre de su pasillo y departamento de Instacart."""
    productos = pd.read_csv(raw / "products.csv")
    pasillos = pd.read_csv(raw / "aisles.csv")
    departamentos = pd.read_csv(raw / "departments.csv")
    return productos.merge(pasillos, on="aisle_id").merge(departamentos, on="department_id")


def cargar_lineas_de_pedido(raw: Path) -> pd.DataFrame:
    """Líneas de los pedidos 'train': qué producto lleva cada pedido y en qué orden."""
    return pd.read_csv(
        raw / "order_products__train.csv",
        usecols=["order_id", "product_id", "add_to_cart_order"],
    )


def elegir_productos(catalogo: pd.DataFrame, lineas: pd.DataFrame) -> pd.DataFrame:
    """Los productos más pedidos de cada zona, uno por ubicación de estante."""
    demanda = lineas["product_id"].value_counts().rename("pedidos")
    catalogo = catalogo.join(demanda, on="product_id").fillna({"pedidos": 0})

    elegidos = []
    for zona, datos in config.ZONAS.items():
        de_la_zona = catalogo[catalogo["department"].isin(datos["departamentos"])]
        top = de_la_zona.nlargest(config.UBICACIONES_POR_ZONA, "pedidos").copy()
        top["zona"] = zona
        elegidos.append(asignar_ubicaciones(top, datos["departamentos"]))
    return pd.concat(elegidos, ignore_index=True)


def asignar_ubicaciones(productos: pd.DataFrame, departamentos: list[str]) -> pd.DataFrame:
    """Coloca los productos de una zona en sus estantes, agrupados por familia.

    Los productos se ordenan por departamento y pasillo de Instacart, y se
    llenan los estantes en orden: pasillo 1 posición 1 izquierda, luego
    derecha, luego posición 2, y así. Productos de la misma familia quedan
    juntos, como en un almacén real.
    """
    orden_dep = {d: i for i, d in enumerate(departamentos)}
    productos = productos.assign(_dep=productos["department"].map(orden_dep))
    productos = productos.sort_values(["_dep", "aisle", "pedidos"], ascending=[True, True, False])
    productos = productos.drop(columns="_dep").reset_index(drop=True)

    i = productos.index
    productos["pasillo"] = i // (config.POSICIONES_POR_PASILLO * 2) + 1
    productos["posicion"] = (i // 2) % config.POSICIONES_POR_PASILLO + 1
    productos["lado"] = ["I" if k % 2 == 0 else "D" for k in i]
    productos["ubicacion"] = [
        id_estante(z, p, q, l)
        for z, p, q, l in zip(productos["zona"], productos["pasillo"],
                              productos["posicion"], productos["lado"])
    ]
    return productos


def id_estante(zona: str, pasillo: int, posicion: int, lado: str) -> str:
    """Identificador de una ubicación de estante, p. ej. 'A03-12-I'."""
    return f"{zona}{pasillo:02d}-{posicion:02d}-{lado}"


def elegir_pedidos(lineas: pd.DataFrame, productos: pd.DataFrame) -> pd.DataFrame:
    """Pedidos de 2 o más productos en los que todos los productos están en el almacén."""
    en_almacen = lineas["product_id"].isin(productos["product_id"])
    por_pedido = en_almacen.groupby(lineas["order_id"]).agg(["all", "size"])
    validos = por_pedido[por_pedido["all"] & (por_pedido["size"] >= 2)].index
    pedidos = lineas[lineas["order_id"].isin(validos)]
    return pedidos.sort_values(["order_id", "add_to_cart_order"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw", type=Path, default=config.DATA_RAW,
                        help="carpeta con los CSV originales de Instacart")
    args = parser.parse_args()

    catalogo = cargar_catalogo(args.raw)
    lineas = cargar_lineas_de_pedido(args.raw)
    productos = elegir_productos(catalogo, lineas)
    pedidos = elegir_pedidos(lineas, productos)

    config.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    columnas = ["ubicacion", "zona", "pasillo", "posicion", "lado", "product_id",
                "product_name", "aisle", "department", "pedidos"]
    productos[columnas].astype({"pedidos": int}).to_csv(
        config.DATA_PROCESSED / "productos.csv", index=False)
    pedidos.to_csv(config.DATA_PROCESSED / "pedidos.csv", index=False)

    cubiertas = lineas["product_id"].isin(productos["product_id"]).mean()
    print(f"Catálogo Instacart: {len(catalogo):,} productos")
    print(f"Productos en el almacén: {len(productos):,} "
          f"({cubiertas:.1%} de las líneas de pedido)")
    print(f"Pedidos completos en el almacén: {pedidos['order_id'].nunique():,} "
          f"de {lineas['order_id'].nunique():,}")


if __name__ == "__main__":
    main()
