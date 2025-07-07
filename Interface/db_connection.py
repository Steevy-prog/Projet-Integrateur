import datetime
import psycopg2
import re
from psycopg2 import Error

class ConnectionDB():
    def __init__(self):

        self.connection_info_center = [
            {
                'host' : "dpg-d197j2nfte5s73c3e07g-a.virginia-postgres.render.com",
                'database' : "projet_integrateur",
                'user' : "group13",
                'password' : "nTUJjJMX36MQ8yRdGVvTqA07nF55YJB3",
                'port' : 5432
            },{
                'host' : "dpg-d1b612gdl3ps73eapfr0-a.oregon-postgres.render.com",
                'database' : "test_bpdd",
                'user' : "test",
                'password' : "w95g3tjqj0S9DLwNiaFEMb1SACWuuIjh",
                'port' : 5432
            },{
                'host' : "dpg-d1c2p8muk2gs73a9onng-a.oregon-postgres.render.com",
                'database' : "steevy1",
                'user' : "steevy",
                'password' : "T0vTIntru5D9SqS1qWnp2nxp7B9aOaWw",
                'port' : 5432
            }
        ]

    def retrieve_connection_info(self, db_connection = None):
        dsn_string = db_connection.dsn
        host_match = re.search(r"host=([^ ]+)", dsn_string)
        retrieved_host = host_match.group(1) if host_match else "N/A"
        if retrieved_host:
            for connection_info in self.connection_info_center:
                if connection_info['host'] == retrieved_host:
                    password = connection_info['password']
                    user = connection_info['user']
                    host = connection_info['host']
                    database = connection_info['database']
                    port = connection_info['port']
                    info = {
                    'db_connection' : db_connection,
                    'host': host,
                    'user' : user,
                    'password' : password,
                    'database' : database,
                    'port' : port
                    }
                    break
            return info

    def connection(self, db_connection = None):
        connection_errors = []
        time = None
        level = None
        message = None
        if db_connection:
            info = self.retrieve_connection_info(db_connection)
            return info
        
        else:
            for connection_info in self.connection_info_center:
                try:
                    db_connection = psycopg2.connect(
                        host = connection_info['host'],
                        database = connection_info['database'],
                        user = connection_info['user'],
                        password = connection_info['password'],
                        port = connection_info['port']
                    )
                    if db_connection:
                        break
                except Exception as e:
                    level = "WARN"
                    message = f"{e}"
                    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    connection_errors.append({'time': time, 'level': level, 'message': message})
                    continue
                except Error as e:
                    level = "ERROR"
                    message = f"{e}"
                    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    connection_errors.append({'time': time, 'level': level, 'message': message})
                    continue
                
            if db_connection:
                if len(connection_errors) > 0:
                    for connection_error in connection_errors:
                        try:
                            cursor = db_connection.cursor()
                            query = "CALL \"EMIR\".Logs_INS(%s, %s, %s)"
                            cursor.execute(query, (connection_error['level'], connection_error['message'], connection_error['time'],))
                            cursor.commit()
                            cursor.close()
                        except:
                            db_connection.rollback()
                info = self.retrieve_connection_info(db_connection)       
                return info
            else:
                return None
