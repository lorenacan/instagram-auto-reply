import instaloader
L = instaloader.Instaloader()
L.load_session_from_file(USERNAME)
import time
import instaloader
from instagram_private_api import Client, ClientCompatPatch
from flask import Flask, request, jsonify, render_template
import threading

app = Flask(__name__, template_folder="templates")

# Credenciales de Instagram (se cambiarán después en Render)
USERNAME = "tu_usuario"
PASSWORD = "tu_contraseña"

# Mensaje automático
AUTO_REPLY_MESSAGE = "¡Gracias por tu comentario! Te responderemos pronto. 😊"

# Iniciar sesión
L = instaloader.Instaloader()
L.login(USERNAME, PASSWORD)

api = Client(USERNAME, PASSWORD)

def get_latest_comments(post_url):
    """ Obtiene los últimos comentarios de una publicación """
    post_id = L.get_post_id_from_shortcode(post_url.split('/')[-2])
    comments = api.media_comments(post_id)
    return comments["comments"]

def reply_to_comment(comment_id, username):
    """ Responde automáticamente a un comentario específico """
    api.post_comment(comment_id, AUTO_REPLY_MESSAGE)
    print(f"Respuesta enviada a {username}")

@app.route("/")
def home():
    """ Renderiza la interfaz de usuario """
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    """ Recibe notificaciones de nuevos comentarios """
    data = request.json
    if "comment_id" in data and "username" in data:
        reply_to_comment(data["comment_id"], data["username"])
        return jsonify({"status": "success"}), 200
    return jsonify({"error": "invalid data"}), 400

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(port=5000, debug=True, use_reloader=False)).start()

