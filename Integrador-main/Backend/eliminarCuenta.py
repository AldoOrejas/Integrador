from flask import Flask, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = 'tu_secreto'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para borrar tu cuenta.')
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    if request.method == 'POST':
        password = request.form['password']

        # Verifica si la contraseña ingresada es correcta
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if user is None:
            flash('Usuario no encontrado.')
            return redirect(url_for('profile'))

        if check_password_hash(user['password'], password):
            # Borra la cuenta del usuario
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            session.clear()  # Cierra la sesión

            flash('Tu cuenta ha sido eliminada exitosamente.')
            return redirect(url_for('index'))
        else:
            flash('Contraseña incorrecta.')

    return '''
        <form method="post">
            <label for="password">Confirma tu contraseña para borrar la cuenta:</label>
            <input type="password" name="password" id="password" required>
            <button type="submit">Eliminar cuenta</button>
        </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Aquí va el código para manejar el inicio de sesión
    pass

@app.route('/profile')
def profile():
    # Aquí va el perfil del usuario
    pass

@app.route('/')
def index():
    return 'Página principal'

if __name__ == '__main__':
    app.run(debug=True)

#Todo esto es una prueba que ni siquera esta vinculada a la database o pagina principal en el html.