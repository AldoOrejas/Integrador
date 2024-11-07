import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
import re
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'webpage'
app.secret_key = 'mi_llave_secreta'
# Folder to store uploaded images
UPLOAD_FOLDER = 'static/img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/signin', methods=['POST'])
def signup():
    # Obtener datos del formulario
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    email = request.form['email']
    address = request.form['address']
    zip_code = request.form['zip']
    job = request.form.get('job')  # radio button (Student o Employee)
    phone = request.form['phone']
    password = request.form['password']
    curp = request.form['curp']
    
    # Validación básica
    if len(phone) != 10 or not phone.isdigit():
        return "El teléfono debe tener 10 dígitos y solo números."
    
    if len(curp) != 18 or not curp.isalnum():
        return "El CURP debe tener 18 caracteres alfanuméricos."

    # Encriptar la contraseña
    hashed_password = generate_password_hash(password)
    
    try:
        # Conectar a la base de datos
        cur = mysql.connection.cursor()
        
        # Llamar al procedimiento almacenado 'AgregarEstudiante'
        cur.callproc('AgregarEstudiante', [first_name, last_name, None, email, phone, hashed_password, curp])
        
        # Confirmar transacción
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('success'))
    
    except Exception as e:
        print(f"Error: {e}")
        return "Ocurrió un error, por favor inténtelo nuevamente."

@app.route('/success')
def success():
    return "¡Cuenta creada con éxito!"


app.run(debug=True)