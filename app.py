# app.py – Punto de entrada: crea la aplicación Flask y registra los blueprints
from flask import Flask
from flask_cors import CORS

from presentation.routes import webhook_bp
from database.appointment_repo import init_db
from config import validate_config, EMAIL_SENDER, ENGINEER_EMAIL


def create_app() -> Flask:
    """Factory que crea y configura la aplicación Flask."""
    validate_config()
    application = Flask(__name__)
    CORS(application)
    application.register_blueprint(webhook_bp)
    init_db()

    # Log de configuración al arrancar
    dest_ingeniero = ENGINEER_EMAIL or EMAIL_SENDER
    print(f"[startup] Email remitente : {EMAIL_SENDER}", flush=True)
    print(f"[startup] Email ingeniero : {dest_ingeniero}", flush=True)
    print(f"[startup] Modo correo     : Gmail API (HTTPS)", flush=True)

    return application


app = create_app()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
