# Datos originales (no se suben al repositorio)

Aquí van los CSV originales del dataset **Instacart Market Basket Analysis**. Pesan
unos 700 MB, más de lo que GitHub acepta, por eso no se versionan.

**No hace falta descargarlos para trabajar.** La versión reducida que usa el
proyecto ya está en `data/processed/`. Solo se necesitan para regenerarla.

## Cómo obtenerlos

1. Entrar a <https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis>
   con una cuenta de Kaggle.
2. Clic en **Download** y descomprimir el `.zip` en esta carpeta.
3. Deben quedar estos archivos:

   ```
   data/raw/aisles.csv
   data/raw/departments.csv
   data/raw/products.csv
   data/raw/orders.csv
   data/raw/order_products__prior.csv
   data/raw/order_products__train.csv
   ```

También se puede dejar la carpeta en otro lugar e indicarla al ejecutar:

```
python src/dataset.py --raw C:/ruta/a/instacart
```
