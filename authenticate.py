import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials # <-- Importación necesaria para JSON

# Se agrega gmail.send para enviar correos vía Gmail API (evita bloqueo SMTP en Render)
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send',
]

def authenticate_google_calendar():
    """
    Autentica con la API de Google Calendar y genera el archivo token.json.
    """
    creds = None
    # 1. Intentar leer desde el JSON en lugar del pickle
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Iniciando el flujo de autenticación de Google...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # 2. Guardar como texto JSON en lugar de binario
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("¡Autenticación exitosa! El archivo 'token.json' ha sido creado.")
    else:
        print("El token de autenticación ya existe y es válido.")
        
    return build('calendar', 'v3', credentials=creds)

if __name__ == '__main__':
    authenticate_google_calendar()
