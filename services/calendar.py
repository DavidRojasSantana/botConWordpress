# services/calendar.py – Wrapper de Google Calendar API
import os
import json
from datetime import datetime

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from config import SCOPES


class GoogleCalendarManager:
    """Gestiona autenticación y operaciones en Google Calendar."""

    def __init__(self, token_path: str = 'token.json',
                 credentials_path: str = 'credentials.json',
                 calendar_id: str = 'primary',
                 tz_offset: str = '-05:00'):
        # token.json y credentials.json viven en la raíz del proyecto
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.token_path       = os.path.join(root, token_path)
        self.credentials_path = os.path.join(root, credentials_path)
        self.calendar_id      = calendar_id
        self.tz_offset        = tz_offset
        self._service         = None

    # ── Autenticación ─────────────────────────────────────────────────────────
    def authenticate(self):
        if self._service:
            return self._service

        creds = None

        # Opción 1: token como variable de entorno JSON (recomendado en Render)
        token_json_str = os.getenv('TOKEN_JSON')
        if token_json_str:
            creds = Credentials.from_authorized_user_info(
                json.loads(token_json_str), SCOPES
            )
        # Opción 2: archivo token.json (local o Render Secret File)
        elif os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            dir_token = os.path.dirname(self.token_path)
            if os.path.isdir(dir_token):
                with open(self.token_path, 'w') as f:
                    f.write(creds.to_json())

        if not creds or not creds.valid:
            raise RuntimeError(
                "No hay token válido. Define TOKEN_JSON en Render "
                "o sube token.json como Secret File."
            )

        self._service = build('calendar', 'v3', credentials=creds)
        return self._service

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _rfc3339(self, dt: datetime) -> str:
        return dt.strftime(f'%Y-%m-%dT%H:%M:%S{self.tz_offset}')

    # ── Operaciones ───────────────────────────────────────────────────────────
    def is_available(self, start: datetime, end: datetime) -> bool:
        """Retorna True si no hay eventos en la franja [start, end)."""
        svc    = self.authenticate()
        result = svc.events().list(
            calendarId=self.calendar_id,
            timeMin=self._rfc3339(start),
            timeMax=self._rfc3339(end),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return len(result.get('items', [])) == 0

    def create_event(self, name: str, contact_number: str, email: str,
                     start: datetime, end: datetime,
                     servicio: str = '') -> dict:
        """Crea el evento e invita al cliente por correo (sendUpdates='all').
        El servicio de interés aparece en el título y en la descripción del evento.
        """
        svc         = self.authenticate()
        fecha_texto = start.strftime('%d/%m/%Y a las %H:%M')
        srv_txt     = servicio if servicio else 'Consulta general'

        event = {
            # Título visible en el calendario: incluye el tema de la reunión
            'summary': f'Cita – {name} | {srv_txt}',
            # Descripción completa con todos los datos del cliente
            'description': (
                f'📋 Tema de la reunión: {srv_txt}\n\n'
                f'👤 Cliente: {name}\n'
                f'📞 Contacto: {contact_number}\n'
                f'📧 Correo: {email}\n\n'
                f'📅 Agendado el: {start.strftime("%d/%m/%Y")} a las {start.strftime("%H:%M")}\n'
                f'— Chatbot de Proyectos Web'
            ),
            'start': {'dateTime': self._rfc3339(start), 'timeZone': 'America/Bogota'},
            'end':   {'dateTime': self._rfc3339(end),   'timeZone': 'America/Bogota'},
            'attendees': [{'email': email, 'displayName': name}],
        }
        return svc.events().insert(
            calendarId=self.calendar_id,
            body=event,
            sendUpdates='all'
        ).execute()
