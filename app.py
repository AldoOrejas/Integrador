from flask import Flask, render_template #aqui mando a  llamr a Flask
from flask_mysqldb import MySQL

#aqui voy a crear una instancia de Flask
app=Flask(__name__)

#aqui haré una instancia de mysql
mysql=MySQL() 

#Aqui configuro los parametros de mi database
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_PORT"]=3306
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="webpage3"
#app.config["MYSQL_HOST"]="localhost"

#vamos a inicializar para que se ejecute la conexion
mysql.init_app(app)

#Aqui van las rutas. osea mis enlaces
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/promos")
def index_promos():
    querito = "SELECT * FROM promos"
    conexion=mysql.connection
    cursor=conexion.cursor()
    cursor.execute(querito)

    resultados=cursor.fetchall()
    print(resultados)




    return render_template("promos/promos.html")



#Activar el modo debug unicamente en desarrollo/oruebas NO PRODUCCION
if __name__ == "__main__":
    app.run(debug=True)



