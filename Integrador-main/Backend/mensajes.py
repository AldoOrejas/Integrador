from flask import Flask, request, jsonify

app = Flask(__name__)

# Ruta principal para recibir el mensaje
@app.route('/send_message', methods=['POST'])
def send_message():
    # Obtener el mensaje enviado desde el frontend
    message = request.form.get('message')

    # Puedes hacer algo con el mensaje aquí, como almacenarlo o procesarlo
    if message:
        return jsonify({"status": "success", "message": "Message received", "content": message})
    else:
        return jsonify({"status": "error", "message": "No message received"}), 400

if __name__ == '__main__':
    app.run(debug=True)
