## Para ejecutar el app.py:
## Haga un entorno virtual 'virtualenv NombreDelEntorno'
## Active el entorno: NombreDelEntorno/script/activate
## ejecute 'pip install -r requirements.txt' para instalar las librerias
## Ejecute 'python .\app.py'

from flask import Flask, jsonify, request, render_template
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

@app.route('/login', methods=['POST'])
def login():
    correo = request.form['correo']
    password = request.form['password']
    conn = get_db_connection()
    cur = conn.cursor(as_dict=True)
    cur.execute("SELECT * FROM SchPersona.tbCredencialesOnline WHERE correo = %s", (correo,))
    user = cur.fetchone()
    
    if user is None:
        return jsonify({'message': 'User not found'}), 404
    
    passw = Fernet(key).decrypt(user['contrasena'])
    
    if password != passw:
        return jsonify({'message': 'Invalid password'}), 401
    
    cur.close()
    conn.close()

    return render_template('dashboard.html')
    
    
@app.route('/administrador')
def admin():
    return render_template('administrador.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/usuario')
def usuario():
    return render_template('usuario.html')


@app.get('/api/users')
def get_users():
    conn = get_db_connection()
    cur = conn.cursor(as_dict=True)
    cur.execute("SELECT * FROM SchCompras.tbEmpleado")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(users)

#Consultas para todos los registros
## Falta completar
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

@app.route('/')
def home():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True, port=3000)