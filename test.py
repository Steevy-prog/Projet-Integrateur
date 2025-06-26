import psycopg2
import pandas as pd


def __main__():
    idorg = 'OABCDE'
    
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="steevy",
        port=5432
    )
    cur = conn.cursor()
    cur.execute("SELECT (p).* FROM \"EMIR\".Produit_EVA() AS p;")
    products = cur.fetchall()
    print(f"Number of rows fetched: {len(products)}")
    if len(products) == 0:
        print("No products loaded from the database. Generating dummy product data.")
        products_df = pd.DataFrame(
                [
                    ('P001', 'SupplierA', 'Dummy Product 1', 'Desc 1', 10.0, 'BrandX', 'ModelA', 'Electronics'),
                    ('P002', 'SupplierB', 'Dummy Product 2', 'Desc 2', 20.0, 'BrandY', 'ModelB', 'Furniture')
                ],
                columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire', 'Brand', 'Model', 'Category']
            )
    else:
        products_df = pd.DataFrame(products, columns=['ID', 'Fourniseur', 'Name', 'Description', 'Prix Unitaire', 'Brand', 'Model', 'Category'])

    for product in products_df.itertuples():
        print(f"Product ID: {product.ID}, Name: {product.Name}")

    cur.close()
    conn.close()
if __name__ == "__main__":
    __main__()