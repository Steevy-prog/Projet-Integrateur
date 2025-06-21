import psycopg2    
from psycopg2 import Error

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

query_1 = """
            DROP TABLE IF EXISTS Users;
            CREATE TABLE Users (
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                access_level VARCHAR(20) NOT NULL
            );
            """
try:
  cursor = db_connection.cursor()
  cursor.execute(query_1)
  db_connection.commit()
  print("Table 'user' created successfully.")
except Error as e:
  print(f"Error creating table 'User': {e}")
  db_connection.rollback()
finally:
  cursor.close()

sample_users_data = [
                {
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'username': 'johndoe',
                    'access_level': 'Employee'
                },
                {
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'username': 'janesmith',
                    'access_level': 'Employee'
                },
                {
                    'first_name': 'Peter',
                    'last_name': 'Jones',
                    'username': 'pjones',
                    'access_level': 'Admin'
                },
                {
                    'first_name': 'Alice',
                    'last_name': 'Williams',
                    'username': 'alicew',
                    'access_level': 'Employee'
                },
                {
                    'first_name': 'Bob',
                    'last_name': 'Brown',
                    'username': 'bbrown',
                    'access_level': 'Employee'
                },
                {
                    'first_name': 'Charlie',
                    'last_name': 'Davis',
                    'username': 'cdavis',
                    'access_level': 'Admin'
                }
            ]
for user in sample_users_data:
    query_2 = f"""
                INSERT INTO Users (first_name, last_name, username, access_level)
                VALUES ('{user['first_name']}', '{user['last_name']}', '{user['username']}', '{user['access_level']}')
                """
    try:
        cursor = db_connection.cursor()
        cursor.execute(query_2)
        db_connection.commit()
        print(f"User {user['username']} added successfully.")
    except Error as e:
        print(f"Error inserting User {user['username']}: {e}")
    finally:
        cursor.close()
