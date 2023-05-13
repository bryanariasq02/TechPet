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
from database import *
import hashlib

load_dotenv()

app = Flask(__name__)
key = Fernet.generate_key()


print(server,database,usuario,password)


# Llamada a la función para probar la conexión

@app.route('/login', methods=['POST'])
def login():
    rol = request.form['option']
    correo = request.form['correo']
    password = request.form['password']

    print(rol)
    if(rol == 'Cliente'):
        # Realizar la consulta a la base de datos para obtener el registro del usuario
        cur.execute("SELECT correo, contrasena FROM SchPersona.tbCliente WHERE correo = %s", (correo))
    elif (rol == 'Administrador'):
        cur.execute("SELECT correo, contrasena FROM SchPersona.tbAdmin WHERE correo = %s", (correo))
    elif (rol == 'Vendedor'):
        cur.execute("SELECT correo, contrasena FROM SchCompras.tbVendedor WHERE correo = %s", (correo))
    elif (rol == 'Empleado'):
        cur.execute("SELECT correo, contrasena FROM SchCompras.tbEmpleado WHERE correo = %s", (correo))

    users = cur.fetchall()

    if users is None:
        # No se encontró un registro para el correo electrónico proporcionado
        error = "Correo electrónico no válido"
        return render_template('login.html')
    
    for user in users:

        stored_password_hash = user['contrasena']

    # Generar el hash de la contraseña proporcionada
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        if password_hash == stored_password_hash:
            
            if rol == 'Cliente':
                return render_template('/cliente.html', correo = user['correo'])
            elif rol == 'Empleado':
                return render_template('/vendedor.html')
            elif rol == 'Administrador':
                return render_template('/administrador.html')
            elif rol == 'Vendedor':
                return render_template('/vendedor.html')
        else:
            # Contraseña incorrecta
            error = "Contraseña incorrecta"
            return render_template('login.html', error=error)


@app.route('/register', methods=['POST'])
def register():
    nombre = request.form['nombre']
    cedula = request.form['cc']
    fecha = request.form['fecha']
    ciudad = request.form['ciudad']
    correo = request.form['correo']
    password = request.form['password']

    password = hashlib.sha256(password.encode()).hexdigest()
    cur.execute("INSERT INTO SchPersona.tbCliente (Nombre, Cedula, Fecha_nacimiento, ciudad, correo, contrasena) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre, cedula, fecha, ciudad, correo, password))

    conn.commit()
    return render_template('cliente.html', correo = correo)
    
@app.route('/registeri')
def registerPage():
    return render_template('register.html')
    
@app.route('/administrador')
def admin():
    return render_template('administrador.html')

@app.route('/dashboard')
def dash():
    return render_template('dashboard.html')

@app.route('/cliente')
def usuario():
    return render_template('cliente.html')

@app.route('/error')
def error():
    return render_template('404.html')

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/vendedor')
def vendedor():
    return render_template('vendedor.html')

@app.route('/compra')
def compra():
    return render_template('compra.html')

@app.route('/venta')
def venta():
    return render_template('venta.html')

@app.route('/verLocales')
def VerLocales():
    return render_template('locales.html')

@app.route('/verProductos')
def VerProductos():
    return render_template('productos.html')

@app.route('/verProveedores')
def VerProveedores():
    return render_template('proveedores.html')

@app.route('/verUsuarios')
def VerUsuarios():
    return render_template('usuarios.html')

@app.route('/verVendedores')
def VerVendedores():
    return render_template('vendedores.html')

@app.route('/verVentas')
def VerVentas():
    return render_template('ventas.html')

@app.get('/api/users')
def get_users():
    cur.execute("SELECT * FROM SchCompras.tbEmpleado")
    users = cur.fetchall()
    return jsonify(users)

#Consultas para todos los registros
## Falta completar
@app.get('/api/table/<id>')
def get_user(id):
    cur.execute("SELECT * FROM %s",(id,))
    user = cur.fetchone()

    if user is None:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(user)

if __name__ == '__main__':
    app.run(debug=True, port=3000)