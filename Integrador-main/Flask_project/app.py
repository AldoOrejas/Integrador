from flask import Flask

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Definir una ruta para la página de inicio
@app.route('/')
def home():
    return "¡Hola, este es un servidor web básico con Flask!"

# Asegurarse de que la aplicación se ejecute cuando se ejecuta el archivo
if __name__ == '__main__':
    app.run(debug=True)
