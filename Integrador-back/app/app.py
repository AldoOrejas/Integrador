import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64

app = Flask(__name__)

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'webpage'
app.secret_key = 'mi_llave_secreta'

# Carpeta para almacenar imágenes subidas
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

# Ruta de inicio
@app.route('/')
def home():
    return render_template('home.html')

# Función para encriptar la contraseña usando AES
def encrypt_password(password, secret_key):
    iv = os.urandom(16)  # Generar un IV aleatorio
    padder = padding.PKCS7(128).padder()
    padded_password = padder.update(password.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(secret_key.encode()), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_password = encryptor.update(padded_password) + encryptor.finalize()

    # Concatenar IV + contraseña encriptada y codificar en base64
    encrypted_password_with_iv = iv + encrypted_password
    return base64.b64encode(encrypted_password_with_iv).decode()  # Convertir a string base64
# Función para desencriptar la contraseña

def decrypt_password(encrypted_password, secret_key):
    # Asegurarse de que la contraseña encriptada es una cadena base64 válida
    if len(encrypted_password) % 4 != 0:
        encrypted_password += "=" * (4 - len(encrypted_password) % 4)

    # Decodificar la contraseña en base64
    encrypted_password = base64.b64decode(encrypted_password)

    # Extraer el IV y el texto cifrado
    iv = encrypted_password[:16]  # Los primeros 16 bytes son el IV
    encrypted_password = encrypted_password[16:]  # El resto es el texto cifrado

    # Configuración del cifrado AES en modo CBC
    cipher = Cipher(algorithms.AES(secret_key.encode()), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_password = decryptor.update(encrypted_password) + decryptor.finalize()

    # Eliminar el padding PKCS7
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_password = unpadder.update(decrypted_password) + unpadder.finalize()

    return unpadded_password.decode()

# Ruta para el registro de nuevos usuarios
@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        age = request.form['age']
        phone = request.form['phone']
        password = request.form['password']
        curp = request.form['curp']
        job_type = request.form['job']  # 'Student' o 'Employeer'

        # Validar que todos los campos estén completos
        if not all([first_name, last_name, email, age, phone, password, curp, job_type]):
            flash('Todos los campos son obligatorios', 'danger')
            return render_template('signin.html')

        # Encriptar la contraseña
        encrypted_password = encrypt_password(password, app.secret_key)

        cursor = mysql.connection.cursor()

        if job_type == 'Student':
            cursor.execute("""
                INSERT INTO tuserstudent (Name, LastName, Age, Mail, Phone, Active, CreatedAt, Calification, Password, CURP, reportcount)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s)
            """, (first_name, last_name, age, email, phone, 1, 0, encrypted_password, curp, 0))
        elif job_type == 'Employeer':
            cursor.execute("""
                INSERT INTO tuserother (Name, LastName, Age, Mail, Phone, Active, CreatedAt, OtherCalification, Password, CURP, reportcount)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s)
            """, (first_name, last_name, age, email, phone, 1, 0, encrypted_password, curp, 0))

        mysql.connection.commit()
        flash('Cuenta creada exitosamente, por favor inicia sesión', 'success')
        return redirect(url_for('login_page'))

    return render_template('signin.html')


# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()

        # Verificar usuario en la base de datos para estudiantes
        cursor.execute("SELECT * FROM tuserstudent WHERE Mail = %s", (email,))
        student = cursor.fetchone()

        if student:
            # Desencriptar la contraseña almacenada en la base de datos
            decrypted_password = decrypt_password(student[9], app.secret_key)  # Contraseña en el índice 9
            if decrypted_password != password:
                flash("Contraseña incorrecta.", "danger")
                return redirect(url_for('login_page'))

            if student[6] == 0:  # Verificar si 'Active' es 0
                flash("Tu cuenta está desactivada. Contacta al administrador.", "danger")
                return redirect(url_for('home'))

            session['user_id'] = student[0]  # Guardar el id del usuario en la sesión
            session['user_name'] = student[1]  # Suponiendo que el nombre está en la primera columna
            session['user_type'] = 'student'  # Indicamos que es un estudiante
            return redirect(url_for('interfazestudiante'))  # Redirigir a la interfaz del estudiante

        # Verificar usuario en la base de datos para empleadores
        cursor.execute("SELECT * FROM tuserother WHERE Mail = %s", (email,))
        employer = cursor.fetchone()

        if employer:
            try:
                # Desencriptar la contraseña almacenada en la base de datos
                decrypted_password = decrypt_password(employer[9], app.secret_key)  # Contraseña en el índice 9
                if decrypted_password != password:
                    flash("Contraseña incorrecta.", "danger")
                    return redirect(url_for('login_page'))

                if employer[6] == 0:  # Verificar si 'Active' es 0
                    flash("Tu cuenta está desactivada. Contacta al administrador.", "danger")
                    return redirect(url_for('home'))  # Redirigir a la página de inicio

                session['user_id'] = employer[0]  # Guardar el id del usuario en la sesión
                session['user_name'] = employer[1]  # Guardar el nombre del empleador
                session['user_type'] = 'employer'  # Indicamos que es un empleador
                return redirect(url_for('interfazempleador'))  # Redirigir a la interfaz del empleador

            except Exception as e:
                flash(f"Error al intentar desencriptar la contraseña: {str(e)}", "danger")
                return redirect(url_for('login_page'))

        flash("Correo o contraseña incorrectos.", "danger")

    return render_template('login.html')  # Renderiza el formulario de inicio de sesión
# Ruta de la interfaz del estudiante
@app.route('/interfazestudiante')
def interfazestudiante():
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    # Obtener los trabajos activos de la tabla tjob
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM tjob WHERE Active = 1 AND idStudent IS NULL")
    jobs = cursor.fetchall()

    return render_template('interfazestudiante.html', jobs=jobs)  # Pasar los empleos al template

@app.route('/mis_trabajos')
def mis_trabajos():
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir si no hay sesión activa
    
    user_id = session['user_id']  # Suponemos que el ID de usuario está en la sesión
    
    # Obtener trabajos activos que el estudiante ha aceptado (Active = 1 y idStudent = user_id)
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT tjob.IdJob, tjob.JobDescription, tjob.job_image, tjob.CreatedAt, tuserother.name AS employer_name, tjob.TUserOther_IdOther
        FROM tjob
        JOIN tuserother ON tjob.TUserOther_IdOther = tuserother.idother
        WHERE tjob.idStudent = %s AND tjob.Active = 1
    """, (user_id,))
    jobs = cursor.fetchall()

    # Si no hay trabajos activos, devolver un mensaje
    if not jobs:
        flash("No tienes trabajos aceptados en este momento.", "warning")

    # Obtener los mensajes asociados a estos trabajos
    jobs_with_chat = []
    for job in jobs:
        job_id = job[0]
        employer_id = job[5]  # El ID del empleador
        job_description = job[1]
        job_image = job[2] if job[2] else 'default_image.png'
        created_at = job[3]
        
        # Consultar los mensajes del chat asociados al trabajo
        cursor.execute("""
            SELECT tchat.message, tchat.timestamp, 
                   CASE 
                       WHEN tchat.idsender IN (SELECT idstudent FROM tuserstudent) 
                       THEN tuserstudent.name 
                       ELSE tuserother.name 
                   END AS sender
            FROM tchat
            LEFT JOIN tuserstudent ON tchat.idsender = tuserstudent.idstudent
            LEFT JOIN tuserother ON tchat.idsender = tuserother.idother
            WHERE tchat.idjob = %s
            ORDER BY tchat.timestamp ASC
        """, (job_id,))
        messages = cursor.fetchall()
        
        # Añadir el trabajo con sus datos y mensajes a la lista como un diccionario
        jobs_with_chat.append({
            'idJob': job_id,
            'description': job_description,
            'job_image': job_image,
            'created_at': created_at,
            'employer_id': employer_id,
            'messages': messages
        })

    return render_template('mis_trabajos.html', jobs_with_chat=jobs_with_chat)

# Ruta de la interfaz del empleador
@app.route('/interfazempleador')
def interfazempleador():
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    # Obtener los trabajos activos del empleador
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT idjob, jobdescription, job_image, createdat, idstudent 
        FROM tjob
        WHERE TUserOther_IdOther = %s AND Active = 1
    """, (session['user_id'],))

    jobs = cursor.fetchall()
    cursor.close()

    return render_template('interfazempleador.html', jobs=jobs)

@app.route('/report_user/<int:reported_user_id>', methods=['GET', 'POST'])
def report_user(reported_user_id):
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    user_id = session['user_id']
    user_type = session.get('user_type', '')

    # Verificar si el usuario que se va a reportar es un estudiante o un empleador
    if user_type == 'student':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tuserother WHERE idother = %s", (reported_user_id,))
        reported_user = cursor.fetchone()
        report_table = 'totherreport'
        user_column = 'idstudent'
        reported_user_column = 'idother'
    elif user_type == 'employer':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tuserstudent WHERE idstudent = %s", (reported_user_id,))
        reported_user = cursor.fetchone()
        report_table = 'tstudentreport'
        user_column = 'idother'
        reported_user_column = 'idstudent'
    else:
        flash("No se puede procesar el reporte.", "danger")
        return redirect(url_for('home'))

    if not reported_user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        description = request.form.get('reportDescription')
        if not description:
            flash("Debe proporcionar una descripción para el reporte.", "danger")
            return render_template('report_user.html', reported_user=reported_user)

        # Insertar el reporte en la tabla correspondiente
        cursor.execute(f"""
            INSERT INTO {report_table} ({user_column}, {reported_user_column}, description, created_at, active)
            VALUES (%s, %s, %s, NOW(), 1)
        """, (user_id, reported_user_id, description))
        
        mysql.connection.commit()
        flash("Reporte enviado exitosamente.", "success")
        return redirect(url_for('interfazempleador'))  # Redirigir a la interfaz del empleador

    return render_template('report_user.html', reported_user=reported_user)@app.route('/mis_trabajos')
def mis_trabajos():
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    user_id = session['user_id']
    
    # Obtener los trabajos aceptados por el estudiante
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT j.idJob, j.JobDescription, j.job_image, j.CreatedAt, j.Active, j.TUserOther_IdOther, j.idStudent, j.IdBuilding, j.reportcount, j.Finished, j.FinishedAt, j.Completed, j.CompletedAt
        FROM tjob j
        WHERE j.idStudent = %s AND j.Active = 1
    """, (user_id,))
    
    jobs = cursor.fetchall()
    jobs_with_chat = []

    # Obtener el estado de chat para cada trabajo
    for job in jobs:
        cursor.execute("""
            SELECT * FROM tchat
            WHERE job_id = %s
        """, (job[0],))  # Usamos el idJob de la tupla
        chat = cursor.fetchone()
        
        jobs_with_chat.append({
            'job': job,
            'has_chat': chat is not None
        })

    return render_template('mis_trabajos.html', jobs_with_chat=jobs_with_chat)



@app.route('/report_employer/<int:reported_user_id>', methods=['GET', 'POST'])
def report_employer(reported_user_id):
    # Verificar si el usuario está logueado
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    user_id = session['user_id']
    user_type = session.get('user_type', '')

    # Inicializar variables
    reported_user = None
    report_table = ''
    user_column = ''
    reported_user_column = ''

    # Verificar el tipo de usuario y procesar el reporte
    if user_type == 'student':
        # El usuario que reporta es un estudiante, reportando a un empleador
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tuserother WHERE idother = %s", (reported_user_id,))
        reported_user = cursor.fetchone()
        report_table = 'totherreport'
        user_column = 'idstudent'
        reported_user_column = 'idother'
    elif user_type == 'employer':
        # El usuario que reporta es un empleador, reportando a un estudiante
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tuserstudent WHERE idstudent = %s", (reported_user_id,))
        reported_user = cursor.fetchone()
        report_table = 'tstudentreport'
        user_column = 'idother'
        reported_user_column = 'idstudent'
    else:
        flash("No se puede procesar el reporte. Usuario no válido.", "danger")
        return redirect(url_for('home'))

    # Verificar si el usuario reportado existe
    if not reported_user:
        flash("Usuario no encontrado.", "danger")
        return redirect(url_for('home'))

    # Procesar el reporte si el formulario fue enviado
    if request.method == 'POST':
        description = request.form.get('reportDescription')  # Obtener la descripción del reporte
        if not description:
            flash("Debe proporcionar una descripción para el reporte.", "danger")
            return render_template('report_employer.html', reported_user=reported_user)  # Volver al formulario

        # Insertar el reporte en la tabla correspondiente
        cursor.execute(f"""
            INSERT INTO {report_table} ({user_column}, {reported_user_column}, description, created_at, active)
            VALUES (%s, %s, %s, NOW(), 1)
        """, (user_id, reported_user_id, description))

        mysql.connection.commit()  # Confirmar los cambios en la base de datos
        flash("Reporte enviado exitosamente.", "success")

        return redirect(url_for('interfazestudiante'))  # Redirigir al inicio del estudiante

    # Renderizar el formulario para el reporte
    return render_template('report_employer.html', reported_user=reported_user)


# Ruta para eliminar trabajo (marcarlo como inactivo)
@app.route('/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    try:
        cursor = mysql.connection.cursor()

        # Verificar si el trabajo tiene un estudiante asignado
        cursor.execute("SELECT idstudent FROM tjob WHERE idjob = %s AND Active = 1", (job_id,))
        result = cursor.fetchone()

        if result:  # Si el trabajo tiene un estudiante asignado
            return redirect(url_for('confirm_completion', job_id=job_id))

        else:  # Si no tiene un estudiante asignado, eliminar directamente
            cursor.execute("UPDATE tjob SET Active = 0 WHERE idjob = %s AND TUserOther_IdOther = %s", (job_id, session['user_id']))
            mysql.connection.commit()
            flash("Trabajo eliminado correctamente.", "success")
            return redirect(url_for('interfazempleador'))  # Redirigir a la interfaz del empleador

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al eliminar el trabajo: {str(e)}", "danger")
        return redirect(url_for('interfazempleador'))

from datetime import datetime

@app.route('/confirm_completion/<int:job_id>', methods=['GET', 'POST'])
def confirm_completion(job_id):
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    if request.method == 'POST':
        status = request.form.get('status')

        cursor = mysql.connection.cursor()

        if status == 'completado':
            # Actualizar el trabajo a completado y agregar el timestamp de completado
            completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                UPDATE tjob 
                SET completed = TRUE, finished = true, completedat = %s 
                WHERE idjob = %s AND TUserOther_IdOther = %s
            """, (completed_at, job_id, session['user_id']))
            mysql.connection.commit()
            
            # Redirigir a la página de calificación del estudiante
            return redirect(url_for('calificar_estudiante', job_id=job_id))  
        
        else:
            # Eliminar el trabajo si no fue completado
            cursor.execute("UPDATE tjob SET Active = 0, finished = true WHERE idjob = %s AND TUserOther_IdOther = %s", (job_id, session['user_id']))
            mysql.connection.commit()
            flash("Trabajo eliminado correctamente.", "success")
            return redirect(url_for('interfazempleador'))  # Redirigir a la interfaz del empleador

    return render_template('confirmacion_completado.html', job_id=job_id)  # Mostrar la página de confirmación

@app.route('/calificar_estudiante/<int:job_id>', methods=['GET', 'POST'])
def calificar_estudiante(job_id):
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    try:
        cursor = mysql.connection.cursor()

        # Obtener el id del estudiante asociado al trabajo
        cursor.execute("SELECT idstudent FROM tjob WHERE idjob = %s", (job_id,))
        result = cursor.fetchone()

        if result:
            student_id = result[0]

            if request.method == 'POST':
                # Obtener la calificación enviada desde el formulario
                calificacion = request.form['calificacion']

                # Llamar al procedimiento almacenado para actualizar la calificación
                cursor.callproc('CalificacionEstudiante', (student_id, float(calificacion)))
                mysql.connection.commit()

                # Marcar el trabajo como inactivo en la tabla tjob (Active = 0)
                cursor.execute("UPDATE tjob SET Active = 0 WHERE idjob = %s", (job_id,))
                mysql.connection.commit()

                flash("Calificación guardada y trabajo marcado como inactivo correctamente.", "success")
                return redirect(url_for('interfazempleador'))  # Redirigir a la interfaz del empleador
        else:
            flash("Trabajo no encontrado o no tiene estudiante asignado.", "danger")
            return redirect(url_for('interfazempleador'))

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al calificar al estudiante o al marcar el trabajo como inactivo: {str(e)}", "danger")
        return redirect(url_for('interfazempleador'))

    # Si el método es GET, renderiza la página para calificar al estudiante
    return render_template('calificar_estudiante.html', job_id=job_id)

# Ruta para agregar trabajo
@app.route('/add_job', methods=['GET', 'POST'])
def add_job():
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    # Si el formulario se envía (POST)
    if request.method == 'POST':
        job_description = request.form['jobDescription']
        building_id = request.form['building']
        job_image = request.files['jobImage']
        print("jobDescription", job_description)
        print("building_id", building_id)
        print("job_image", job_image)
        # Guardar la imagen si existe
        if job_image:
            filename = secure_filename(job_image.filename)
            job_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Insertar el trabajo en la base de datos
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO tjob (jobDescription, IdBuilding, job_image, TUserOther_IdOther, Active, CreatedAt) VALUES (%s, %s, %s, %s, 1, NOW())",
                           (job_description, building_id, filename, session['user_id']))
            mysql.connection.commit()
            flash('Job added successfully!', 'success')
            print("objeto agregado db")
            return redirect(url_for('interfazempleador'))  # Redirigir al listado de trabajos
        

        except Exception as e:
            print("Error al agregar el objeto", e)
            flash(f'Error: {str(e)}', 'danger')

    # Si la solicitud es GET, renderiza el formulario
    cursor = mysql.connection.cursor()
    
    # Modificar la consulta para que solo devuelva edificios asociados al empleador logueado
    cursor.execute("SELECT * FROM tbuilding WHERE idother = %s", (session['user_id'],))  # Filtrar por el id del empleador
    buildings = cursor.fetchall()

    return render_template('add_job.html', buildings=buildings)

# Ruta para aceptar un trabajo
@app.route('/accept_job/<int:job_id>', methods=['POST'])
def accept_job(job_id):
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir si no hay sesión activa

    student_id = session['user_id']  # Obtener el id del estudiante desde la sesión

    try:
        cursor = mysql.connection.cursor()

        # Actualizar la tabla tjob para asignar el estudiante al trabajo
        cursor.execute("UPDATE tjob SET idStudent = %s WHERE idjob = %s AND idStudent IS NULL", (student_id, job_id))
        mysql.connection.commit()

        flash("Trabajo aceptado correctamente.", "success")

    except Exception as e:
        mysql.connection.rollback()
        flash(f"Error al aceptar el trabajo: {str(e)}", "danger")

    return redirect(url_for('interfazestudiante'))  # Redirigir a la interfaz del estudiante
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # Obtener el perfil del estudiante
    cursor.execute("SELECT * FROM tuserstudent WHERE idstudent = %s", (user_id,))
    user = cursor.fetchone()

    if user:
        if request.method == 'POST':
            # Procesar actualización de información del perfil
            updated_name = request.form.get('editName')
            updated_email = request.form.get('editEmail')
            updated_phone = request.form.get('editPhone')

            # Actualizar nombre del estudiante
            if updated_name:
                cursor.execute("""
                    UPDATE tuserstudent
                    SET name = %s
                    WHERE idstudent = %s
                """, (updated_name, user_id))

            # Actualizar correo del estudiante si es necesario
            if updated_email:
                try:
                    cursor.callproc('ActualizarCorreoEstudiante', [user_id, updated_email])
                    mysql.connection.commit()
                    flash("Correo actualizado correctamente", "success")
                except Exception as e:
                    mysql.connection.rollback()
                    flash(f"Error al actualizar el correo: {str(e)}", "danger")

            # Actualizar teléfono del estudiante si es necesario
            if updated_phone:
                try:
                    cursor.callproc('ActualizarNumeroEstudiante', [user_id, updated_phone])
                    mysql.connection.commit()
                    flash("Teléfono actualizado correctamente", "success")
                except Exception as e:
                    mysql.connection.rollback()
                    flash(f"Error al actualizar el teléfono: {str(e)}", "danger")

            # Eliminar la cuenta del estudiante (cambiar 'active' a 0)
            if 'delete_account' in request.form:
                try:
                    cursor.execute("""
                        UPDATE tuserstudent
                        SET active = 0
                        WHERE idstudent = %s
                    """, (user_id,))
                    mysql.connection.commit()
                    flash("Cuenta eliminada correctamente", "success")
                    session.clear()  # Limpiar la sesión del usuario
                    return redirect(url_for('home'))  # Redirigir al inicio

                except Exception as e:
                    mysql.connection.rollback()
                    flash(f"Error al eliminar la cuenta: {str(e)}", "danger")

            # Después de la actualización, volvemos a obtener los datos actualizados del usuario
            cursor.execute("SELECT * FROM tuserstudent WHERE idstudent = %s", (user_id,))
            user = cursor.fetchone()

        # Obtener los reportes del estudiante desde la tabla tstudentreport
        cursor.execute("SELECT * FROM tstudentreport WHERE idstudent = %s", (user_id,))
        reportes = cursor.fetchall()

        # Contar el número total de reportes
        total_reportes = len(reportes)

        # Pasar los reportes y el total de reportes al template
        return render_template('profile.html', user=user, reportes=reportes, total_reportes=total_reportes)

    return redirect(url_for('login_page'))  # Redirigir al login si el estudiante no existe

# Profile Empleador Route
@app.route('/profileother', methods=['GET', 'POST'])
def profileother():
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    # Obtener el perfil del empleador
    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM tuserother WHERE idother = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        flash("No se encontró el perfil de empleador.", "danger")
        return redirect(url_for('home'))  # Redirigir a la página de inicio si no se encuentra el perfil

    if request.method == 'POST':
        # Actualizar nombre
        if 'editName' in request.form:
            new_name = request.form['editName']
            try:
                cursor.execute("UPDATE tuserother SET name = %s WHERE idother = %s", (new_name, user_id))
                mysql.connection.commit()
                flash("Nombre actualizado exitosamente.", "success")
            except Exception as e:
                mysql.connection.rollback()
                flash("Error al actualizar el nombre.", "danger")
        
        # Actualizar correo
        if 'editEmail' in request.form:
            new_email = request.form['editEmail']
            try:
                cursor.callproc('ActualizarCorreoEmpleador', (user_id, new_email))
                mysql.connection.commit()
                flash("Correo actualizado exitosamente.", "success")
            except Exception as e:
                mysql.connection.rollback()
                flash(f"Error al actualizar el correo: {e}", "danger")
        
        # Actualizar teléfono
        if 'editPhone' in request.form:
            new_phone = request.form['editPhone']
            try:
                cursor.callproc('ActualizarNumeroEmpleador', (user_id, new_phone))
                mysql.connection.commit()
                flash("Teléfono actualizado exitosamente.", "success")
            except Exception as e:
                mysql.connection.rollback()
                flash(f"Error al actualizar el teléfono: {e}", "danger")

        # Eliminar cuenta
        if 'delete_account' in request.form:
            try:
                # Establecer 'active' a 0 para desactivar la cuenta
                cursor.execute("UPDATE tuserother SET active = 0 WHERE idother = %s", (user_id,))
                mysql.connection.commit()
                flash("Cuenta eliminada exitosamente.", "success")
                session.clear()  # Eliminar la sesión
                return redirect(url_for('home'))  # Redirigir al inicio
            except Exception as e:
                mysql.connection.rollback()
                flash(f"Error al eliminar la cuenta: {e}", "danger")
        
        return redirect(url_for('profileother'))  # Redirigir a la misma página para mostrar los cambios

    # Obtener los reportes del empleador desde la tabla totherreport
    cursor.execute("SELECT * FROM totherreport WHERE idother = %s", (user_id,))
    reportes = cursor.fetchall()

    # Contar el número total de reportes
    total_reportes = len(reportes)

    # Pasar los reportes y el total de reportes al template
    return render_template('profileother.html', user=user, reportes=reportes, total_reportes=total_reportes)

# Ruta de cierre de sesión
@app.route('/logout')
def logout():
    session.clear()  # Elimina toda la información de la sesión
    return redirect(url_for('home'))  # Redirige al inicio
@app.route('/livechat/<int:job_id>', methods=['GET', 'POST'])
def livechat(job_id):
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir si no hay sesión activa

    cursor = mysql.connection.cursor()

    # Obtener los detalles del trabajo
    cursor.execute("SELECT * FROM tjob WHERE idjob = %s", (job_id,))
    job_details = cursor.fetchone()

    if job_details:
        # Obtener los mensajes asociados a este trabajo
        cursor.execute("""
            SELECT tchat.message, tchat.timestamp, 
                   CASE 
                       WHEN tchat.sender_id IN (SELECT idstudent FROM tuserstudent) 
                       THEN tuserstudent.name 
                       ELSE tuserother.name 
                   END AS sender
            FROM tchat
            LEFT JOIN tuserstudent ON tchat.sender_id = tuserstudent.idstudent
            LEFT JOIN tuserother ON tchat.sender_id = tuserother.idother
            WHERE tchat.idjob = %s
            ORDER BY tchat.timestamp ASC
        """, (job_id,))
        messages = cursor.fetchall()

        # Inicializamos la variable para los nombres de los participantes
        student_name = None
        employer_name = None

        # Obtener los IDs del estudiante y empleador del trabajo
        cursor.execute("SELECT idstudent, tuserother_idother FROM tjob WHERE idjob = %s", (job_id,))
        job_participants = cursor.fetchone()

        # Obtener el nombre del estudiante si existe
        if job_participants and job_participants[0]:
            cursor.execute("SELECT name FROM tuserstudent WHERE idstudent = %s", (job_participants[0],))
            student_name = cursor.fetchone()[0]

        # Obtener el nombre del empleador si existe
        if job_participants and job_participants[1]:
            cursor.execute("SELECT name FROM tuserother WHERE idother = %s", (job_participants[1],))
            employer_name = cursor.fetchone()[0]

        # Obtener el tipo de usuario de la sesión (empleador o estudiante)
        user_type = session.get('user_type', '')

        # Verificar si el usuario tiene acceso al trabajo
        if user_type == 'student':
            cursor.execute("SELECT idstudent FROM tjob WHERE idjob = %s AND idstudent = %s", (job_id, session['user_id']))
            user_job = cursor.fetchone()
            if not user_job:
                flash("No tienes acceso a este trabajo.", "danger")
                return redirect(url_for('interfazestudiante'))  # Redirigir si el estudiante no tiene acceso
        elif user_type == 'employer':
            cursor.execute("SELECT tuserother_idother FROM tjob WHERE idjob = %s AND tuserother_idother = %s", (job_id, session['user_id']))
            user_job = cursor.fetchone()
            if not user_job:
                flash("No tienes acceso a este trabajo.", "danger")
                return redirect(url_for('interfazempleador'))  # Redirigir si el empleador no tiene acceso

        # Asegúrate de que los mensajes no estén vacíos antes de pasarlos
        messages = [{"message": msg[0], "timestamp": msg[1], "sender": msg[2]} for msg in messages]

        # Pasamos los datos a la plantilla
        return render_template('livechat.html', 
                               job_id=job_id, 
                               job=job_details, 
                               messages=messages, 
                               student_name=student_name, 
                               employer_name=employer_name)
    else:
        flash('Trabajo no encontrado', 'danger')
        return redirect(url_for('interfazestudiante'))  # Redirigir si no se encuentra el trabajo

@app.route('/send_message/<int:job_id>', methods=['POST'])
def send_message(job_id):
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir si no hay sesión activa

    message = request.form.get('messageInput')  # Obtener el mensaje del formulario
    if not message:
        flash("No se ha ingresado un mensaje", "danger")
        return redirect(url_for('livechat', job_id=job_id))  # Redirigir si no se ingresa mensaje

    user_id = session['user_id']
    user_type = session.get('user_type', '')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT TUserOther_IdOther, IdStudent FROM tjob WHERE idjob = %s", (job_id,))
    job_details = cursor.fetchone()

    if not job_details:
        flash("Trabajo no encontrado", "danger")
        return redirect(url_for('livechat', job_id=job_id))  # Redirigir si no se encuentra el trabajo

    # Verificar si el sender_id existe en la tabla correspondiente
    sender_id = user_id
    if user_type == 'student':
        cursor.execute("SELECT IdStudent FROM tuserstudent WHERE IdStudent = %s", (sender_id,))
        user_exists = cursor.fetchone()
        if not user_exists:
            flash("El estudiante no existe en la base de datos", "danger")
            return redirect(url_for('livechat', job_id=job_id))
        receiver_id = job_details[0]  # Empleador es el receptor
    else:
        cursor.execute("SELECT IdOther FROM tuserother WHERE IdOther = %s", (sender_id,))
        user_exists = cursor.fetchone()
        if not user_exists:
            flash("El empleador no existe en la base de datos", "danger")
            return redirect(url_for('livechat', job_id=job_id))
        receiver_id = job_details[1]  # Estudiante es el receptor

    try:
        # Solo hacer una inserción: insertar el mensaje con sender_id y receiver_id
        cursor.execute("""
            INSERT INTO tchat (idjob, message, sender_id, receiver_id) 
            VALUES (%s, %s, %s, %s)
        """, (job_id, message, sender_id, receiver_id))

        mysql.connection.commit()
        flash('Mensaje enviado!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al enviar el mensaje: {str(e)}', 'danger')
        print(f"Error al insertar mensaje: {e}")  # Para depuración

    return redirect(url_for('livechat', job_id=job_id))  # Redirigir para mostrar los mensajes actualizados

@app.route('/add_building', methods=['POST'])
def add_building():
    if 'user_name' not in session:
        return redirect(url_for('login_page'))  # Redirigir al login si no hay sesión activa

    if request.method == 'POST':
        # Obtener los datos del formulario
        codigop = request.form['codigop']
        direccion = request.form['direccion']
        user_id = session['user_id']
        print("codigop: ", codigop)
        print("direccion", direccion)
        try:
            cursor = mysql.connection.cursor()

            # Llamar al procedimiento almacenado AgregarEdificio
            cursor.callproc('AgregarEdificio', (user_id, codigop, direccion))
            mysql.connection.commit()

            flash("Edificio agregado correctamente.", "success")
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error al agregar el edificio: {str(e)}", "danger")

        return redirect(url_for('profileother'))  # Redirigir a la página de perfil del empleador

if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)
