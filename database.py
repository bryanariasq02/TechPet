import pymssql
import os
from dotenv import load_dotenv

server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
usuario = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

try:
    # Conexion a la base de datos 
    conn = pymssql.connect(server, usuario, password, database)
    cur = conn.cursor(as_dict=True)
    print("Conexion exitosa a la base de datos: ", conn)

                    
except Exception as e:
    print("Error al conectar con la base de datos SQL Server: ", e)