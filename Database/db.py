from flask import Flask

app = Flask(__name__)

from flask_mysqldb import MySQL

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE'] = 'webpagetres.sql'

mysql = MySQL(app)

@app.route('/')
def index():
    usuarios = mysql.query('SELECT * FROM tuserstudentadult')
    return jsonify(usuarios)

conn = conn.cursor()

cursor.execute('''
    INSERT INTO tuserstudentadult (name, lastname, age)
    VALUES (Abdel, Gutierrez, 19)
''')

conn.commit()

conn.close()
