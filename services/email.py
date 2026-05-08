# services/email.py – Envío de correo vía Gmail API (HTTPS)
#
# ¿Por qué Gmail API y no SMTP?
# Render Free tier bloquea el puerto SMTP (587/465) → Errno 101 Network unreachable.
# La Gmail API usa HTTPS (puerto 443) que siempre está abierto, y reutiliza
# las mismas credenciales OAuth2 de Google Calendar ya configuradas.
import base64
import json
import os
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from config import SCOPES, EMAIL_SENDER, ENGINEER_EMAIL


def _get_gmail_service():
    """Obtiene el servicio Gmail API reutilizando el token de Google Calendar."""
    creds = None
    root  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Opción 1: token como variable de entorno (Render)
    token_json_str = os.getenv('TOKEN_JSON')
    if token_json_str:
        creds = Credentials.from_authorized_user_info(
            json.loads(token_json_str), SCOPES
        )
    # Opción 2: archivo token.json local o Render Secret File
    else:
        token_path = os.path.join(root, 'token.json')
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path = os.path.join(root, 'token.json')
        if os.path.isdir(os.path.dirname(token_path)):
            with open(token_path, 'w') as f:
                f.write(creds.to_json())

    if not creds or not creds.valid:
        raise RuntimeError(
            "No hay token válido para Gmail API. "
            "Regenera token.json con authenticate.py y sube TOKEN_JSON a Render."
        )

    return build('gmail', 'v1', credentials=creds)


def send_email(to: str, subject: str, body: str) -> bool:
    """
    Envía un correo usando Gmail API (HTTPS).
    Requiere scope 'https://www.googleapis.com/auth/gmail.send' en el token.
    """
    remitente = EMAIL_SENDER or 'me'
    print(f"[email] Enviando a {to} | Asunto: {subject[:60]}", flush=True)
    try:
        service = _get_gmail_service()

        msg            = MIMEText(body, 'plain', 'utf-8')
        msg['to']      = to
        msg['from']    = remitente
        msg['subject'] = subject

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
        service.users().messages().send(
            userId='me',
            body={'raw': raw}
        ).execute()

        print(f"[email] ✅ Correo enviado exitosamente a {to}", flush=True)
        return True

    except Exception as e:
        print(f"[email] ❌ Error enviando correo a {to}: {e}", flush=True)
        return False
