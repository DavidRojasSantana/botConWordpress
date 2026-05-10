# config.py – Centraliza todas las variables de entorno y constantes
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ── Telegram ───────────────────────────────────────────────────────────────────
#TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# ── Email ──────────────────────────────────────────────────────────────────────
EMAIL_SENDER   = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
ENGINEER_EMAIL = os.getenv('ENGINEER_EMAIL')   # fallback: EMAIL_SENDER

# ── Google Calendar + Gmail API ───────────────────────────────────────────────
# gmail.send permite enviar correos vía HTTPS (evita el bloqueo SMTP de Render)
CALENDAR_ID = 'primary'
SCOPES      = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send',
]

# ── Base de datos ──────────────────────────────────────────────────────────────
DB_PATH = os.getenv(
    'DB_PATH',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'appointments.db')
)
MONGO_URI = os.getenv('MONGO_URI')

# ── Administración ─────────────────────────────────────────────────────────────
ADMIN_KEY = os.getenv('ADMIN_KEY', 'admin123')

# ── Sesión ─────────────────────────────────────────────────────────────────────
SESSION_TIMEOUT_MINUTES = 10
MAX_PROCESSED_SIZE      = 5000

# ── Franjas horarias de atención (08:00 – 16:00) ──────────────────────────────
HORARIOS = ['08:00', '09:00', '10:00', '11:00', '12:00',
            '13:00', '14:00', '15:00', '16:00']

# ── Saludos reconocidos ────────────────────────────────────────────────────────
SALUDOS = ["hola", "buen dia", "buenos días", "buenas",
           "comenzar", "inicio", "ayuda", "."]

# ── Mapeo estado → nombre de servicio (para correos de resumen) ────────────────
SERVICE_LABELS = {
    'sub_menu_one_page':   'Páginas One Page',
    'sub_menu_multi_page': 'Páginas Multi Page',
    'sub_menu_web_app':    'Aplicación Web',
    'opsisren':            'Optimización del Sistema y Rendimiento',
    'seguElimMa':          'Seguridad y Eliminación de Malware',
    'soprtSofApps':        'Soporte de Software y Aplicaciones',
    'remoto':              'Soporte y Asesoramiento Remoto',
    'chatbot_info':        'Chatbot para WhatsApp', # Lo dejo así asumiendo que vendes bots de WhatsApp
}

# ── Conjuntos de estados para el match-case ────────────────────────────────────
DETAIL_STATES = frozenset({
    'sub_menu_one_page', 'sub_menu_multi_page', 'sub_menu_web_app',
    'remoto', 'soprtSofApps', 'seguElimMa', 'opsisren', 'chatbot_info'
})
AWAITING_STATES = frozenset({
    'awaiting_name', 'awaiting_contact', 'awaiting_email',
    'awaiting_date', 'awaiting_timeslot'
})


def validate_config() -> None:
    """Valida que las variables obligatorias estén presentes. Llamar desde create_app()."""
    required = {
      #  'TELEGRAM_TOKEN':    TELEGRAM_TOKEN,
        'EMAIL_SENDER':      EMAIL_SENDER,
        'EMAIL_PASSWORD':    EMAIL_PASSWORD,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Variables de entorno faltantes: {', '.join(missing)}")