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
import json

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

@app.route('/registervr', methods=['POST'])
def registerVendedor():
    Nombre = request.form['nombre']
    cedula = request.form['cc']
    IDLocal = request.form['IDLocal']
    ciudad = request.form['ciudad']
    correo = request.form['correo']
    password = request.form['password']

    password = hashlib.sha256(password.encode()).hexdigest()
    cur.execute("INSERT INTO SchCompras.tbVendedor (Nombre, Cedula, IDLocal, Ciudad, correo, contrasena) VALUES (%s, %s, %s, %s, %s, %s)",
                (Nombre, cedula, IDLocal, ciudad, correo, password))

    conn.commit()
    return render_template('vendedor.html', correo = correo)

@app.route('/registerv')
def verpaginav():
    return render_template('registerVendedor.html')

@app.route('/registerpr', methods=['POST'])
def registerProveedor():
    Nombre = request.form['nombre']
    Nit = request.form['nit']
    ciudad = request.form['ciudad']

    cur.execute("INSERT INTO SchCompras.tbProveedor (Nombre, Nit, Ciudad) VALUES (%s, %s, %s)",
                (Nombre,Nit, ciudad))

    conn.commit()
    return render_template('administrador.html')

@app.route('/registerp')
def registerProveedorP():
    return render_template('registerProveedor.html')
    
@app.route('/administrador')
def admin():
    return render_template('administrador.html')

@app.route('/dashboard')
def dash():
    cur.execute("""SELECT CAST(YEAR(V.fecha) AS VARCHAR(4)) + '-' + CAST(MONTH(V.fecha) AS VARCHAR(2)) AS fecha,
       cast(sum(AP.Cantidad * P.costo) as int) AS total
        FROM SchVentas.tbVenta AS V
        INNER JOIN SchProduccion.tbAuxProducto AS AP ON V.IDCompra = AP.IDCompra
        INNER JOIN SchProduccion.tbProducto AS P ON P.IDProducto = AP.IDProducto
        group by CAST(YEAR(V.fecha) AS VARCHAR(4)) + '-' + CAST(MONTH(V.fecha) AS VARCHAR(2))""")
    ventasFecha = cur.fetchall()
    ventasFecha = json.dumps(ventasFecha) 
    cur.execute("""SELECT Nombre, count(Nombre) as cantidad
                    FROM SchVentas.tbVenta AS V
                    INNER JOIN SchPersona.tbCliente AS C ON V.IDCliente = C.IDCliente
                    group by Nombre""")
    clientes = cur.fetchall()
    clientes = json.dumps(clientes) 
    cur.execute("""select Descripcion, cantidad from SchProduccion.tbAuxProducto AS AP 
                    INNER JOIN SchProduccion.tbProducto AS P ON P.IDProducto = AP.IDProducto""")
    productos = cur.fetchall()
    
    return render_template('dashboard.html', ventasFecha = ventasFecha, clientes= clientes, productos = productos)

@app.route('/cliente')
def usuario():
    return render_template('cliente.html')

@app.route('/error')
def error():
    return render_template('404.html')

@app.route('/exito')
def exito():
    return render_template('200.html')

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/vendedor')
def vendedor():
    return render_template('vendedor.html')

@app.route('/compra')
def compra():
    return render_template('compra.html')

@app.route('/comprar', methods=['POST'])
def comprar():
    Descripcion = request.form['description']
    fecha = request.form['fecha']
    IDCliente = request.form['IDCliente']
    IDLocal = request.form['IDLocal']
    IDCompra = request.form['IDCompra']

    cur.execute("INSERT INTO SchVentas.tbVenta (IDCliente, IDLocal, IDCompra, Descripcion, fecha) VALUES (%s, %s, %s,%s, %s)",
                (IDCliente, IDLocal, IDCompra, Descripcion, fecha))

    conn.commit()
    return render_template('cliente.html')

@app.route('/vender', methods=['POST'])
def vende():
    IDProducto = request.form['IDProducto']
    cantidad = request.form['cantidad']

    cur.execute("INSERT INTO SchProduccion.tbAuxProducto (IDProducto, cantidad) VALUES (%s, %s)",
                (IDProducto, cantidad))

    conn.commit()
    return render_template('cliente.html')

@app.route('/venta')
def venta():
    return render_template('venta.html')

@app.route('/VerAuxPro')
def compras():
    cur.execute("select * from SchProduccion.tbAuxProducto")
    compras = cur.fetchall()
    return render_template('compras.html', compras = compras)

@app.route('/verLocales')
def VerLocales():
    cur.execute("SELECT Nit, Nombre, Ciudad, Nom_Gerente FROM SchVentas.tbLocales")
    locales = cur.fetchall()
    return render_template('locales.html', locales = locales)

@app.route('/verProductos')
def VerProductos():
    cur.execute("SELECT IDProducto, Descripcion, costo FROM SchProduccion.tbProducto")
    productos = cur.fetchall()
    return render_template('productos.html', productos = productos)

@app.route('/verProveedores')
def VerProveedores():
    cur.execute("SELECT Nit, Nombre, Ciudad FROM SchCompras.tbProveedor")
    proveedores = cur.fetchall()
    return render_template('proveedores.html', proveedores = proveedores)

@app.route('/verUsuarios')
def VerUsuarios():
    cur.execute("""SELECT Nombre, Cedula,correo, 'Cliente' AS Rol
                    FROM SchPersona.tbCliente
                    UNION
                    SELECT Nombre, Cedula,correo, 'Vendedor' AS Rol
                    FROM SchCompras.tbVendedor
                    UNION
                    SELECT Nombre, Cedula,correo, 'Administrador' AS Rol
                    FROM SchPersona.tbAdmin
                    UNION
                    SELECT Nombre, Cedula,correo, 'Empleado' AS Rol
                    FROM SchCompras.tbEmpleado""")
    usuarios = cur.fetchall()
    return render_template('usuarios.html', usuarios = usuarios)

@app.route('/verVendedores')
def VerVendedores():
    cur.execute("""select v.Nombre, v.Cedula, v.Ciudad, l.Nit, l.Nombre as local, l.Nom_Gerente from SchCompras.tbVendedor v
                   inner join SchVentas.tbLocales l
                   on v.IDLocal = l.IDlocal""")
    vendedores = cur.fetchall()
    return render_template('vendedores.html', vendedores=vendedores)

@app.route('/verVentas')
def VerVentas():
    cur.execute("""SELECT V.IDVenta, V.Descripcion,V.fecha, 
	   C.Nombre, C.Cedula, C.ciudad as ciudad_cliente, C.correo, 
	   L.Nombre as local, P.Descripcion as producto, AP.Cantidad, 
	   P.costo as valorU, AP.Cantidad*P.costo as total
       FROM SchVentas.tbVenta AS V
        INNER JOIN SchPersona.tbCliente AS C ON V.IDCliente = C.IDCliente
        INNER JOIN SchVentas.tbLocales AS L ON V.IDLocal = L.IDlocal
        INNER JOIN SchProduccion.tbAuxProducto AS AP ON V.IDCompra = AP.IDCompra
        INNER JOIN SchProduccion.tbProducto AS P ON P.IDProducto = AP.IDProducto""")
    ventas = cur.fetchall()

    return render_template('ventas.html', ventas = ventas)

@app.get('/api/users')
def get_users():
    cur.execute("SELECT * FROM SchCompras.tbEmpleado")
    users = cur.fetchall()
    return jsonify(users)

#Consultas para todos los registros
## Falta completar
@app.get('/api/table/<id>')
def get_user(id):
    cur.execute("SELECT * FROM %s",(id))
    user = cur.fetchone()

    if user is None:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(user)

if __name__ == '__main__':
    app.run(debug=True, port=3000)