from flask import Flask, jsonify, request, send_file
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import pymssql

load_dotenv()

app = Flask(__name__)
key = Fernet.generate_key()

server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
usuario = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

print(server, password)


def get_db_connection():
    try:
        # Conexion a la base de datos
        conn = pymssql.connect(server, usuario, password, database)

    except Exception as e:
        print("Error to connect", e)
    
    return conn

@app.get('/api/users')
def get_users():
    conn = get_db_connection()
    cur = conn.cursor(as_dict=True)
    cur.execute("SELECT * FROM SchCompras.tbEmpleado")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(users)

@app.get('/api/table/<id>')
def get_user(id):
    conn = get_db_connection()
    cur = conn.cursor(as_dict=True)
    cur.execute("SELECT * FROM %s",(id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(user)

@app.get('/')
def home():
    return send_file('static/index.html')

if __name__ == '__main__':
    app.run(debug=True, port=3000)