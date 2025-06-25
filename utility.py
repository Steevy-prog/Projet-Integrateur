import psycopg2
from psycopg2 import Error

def connect_to_db():
  host = "dpg-d1b612gdl3ps73eapfr0-a.oregon-postgres.render.com"  # Replace with your database host
  database = "test_bpdd"  # Replace with your database name
  user = "test"  # Replace with your database username
  password = "w95g3tjqj0S9DLwNiaFEMb1SACWuuIjh"  # Replace with your database password
  port = 5432  # Default PostgreSQL port, change if necessary

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

  except Error as e:
      print(f"Error connecting to PostgreSQL database: {e}")
      
  return db_connection

def generate_serial_id(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("SELECT nextval('serial_id_seq')")
    serial_id = cursor.fetchone()[0]
    cursor.close()
    return serial_id