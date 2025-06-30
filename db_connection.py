import psycopg2
from psycopg2 import Error

host = "dpg-d1b612gdl3ps73eapfr0-a.oregon-postgres.render.com"
database = "test_bpdd"
user = "test"
password = "w95g3tjqj0S9DLwNiaFEMb1SACWuuIjh"
port = 5432


db_connection = None
try:
    db_connection = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password,
        port=port
    )
    print(f"Successfully connected to PostgreSQL database: {database}")

except Exception as e:
    db_connection = psycopg2.connect(
       host="localhost",
       database="postgres",
       user="postgres",
       password="steevy",
       port=5432
    )
    print(f"Error connecting to online PostgreSQL database: {e}")


