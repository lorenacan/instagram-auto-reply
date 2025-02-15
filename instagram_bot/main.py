import time
import instaloader
from instagram_private_api import Client, ClientCompatPatch
from flask import Flask, request, jsonify, render_template
import threading
import os

app = Flask(__name__)

# Credenciales de Instagram (definidas directamente en el código)
INSTAGRAM_USERNAME = "revenia.agency"
INSTAGRAM_PASSWORD = "ArusyLosScoutssonunasecta"

# Imprimir valores de las credenciales para depuración (ocultando la contraseña)
print(f"INSTAGRAM_USERNAME: {INSTAGRAM_USERNAME}")
print("INSTAGRAM_PASSWORD: ********")

# Mensaje automático
AUTO_REPLY_MESSAGE = "¡Gracias por tu comentario! Te responderemos pronto. 😊"

# Iniciar sesión con cookies para evitar bloqueos
L = instaloader.Instaloader()
try:
    L.load_session_from_file(INSTAGRAM_USERNAME)
except FileNotFoundError:
    L.context.log("Iniciando sesión por primera vez...")
    L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    L.save_session_to_file()

try:
    api = Client(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
except Exception as e:
    print(f"Error al iniciar sesión en Instagram: {e}")
    exit()

def get_latest_comments(post_url):
    """ Obtiene los últimos comentarios de una publicación """
    try:
        post_id = L.get_post_id_from_shortcode(post_url.split('/')[-2])
        comments = api.media_comments(post_id)
        return comments['comments']
    except Exception as e:
        print(f"Error al obtener comentarios: {e}")
        return []

def reply_to_comment(comment_id, username):
    """ Responde automáticamente a un comentario específico """
    try:
        api.post_comment(comment_id, AUTO_REPLY_MESSAGE)
        print(f"Respuesta enviada a {username}")
    except Exception as e:
        print(f"Error al responder comentario: {e}")

@app.route('/')
def home():
    """ Renderiza la interfaz de usuario """
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """ Recibe notificaciones de nuevos comentarios """
    data = request.json
    if 'comment_id' in data and 'username' in data:
        reply_to_comment(data['comment_id'], data['username'])
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "invalid data"}), 400

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(port=5000, debug=True, use_reloader=False)).start()

