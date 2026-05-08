# core/state.py – Gestión de estado de usuarios (thread-safe)
import threading
from datetime import datetime
from config import MAX_PROCESSED_SIZE

# ── Almacenamiento en memoria ──────────────────────────────────────────────────
state_lock:         threading.Lock = threading.Lock()
user_state:         dict           = {}   # {number: {state, last_interaction, processing}}
appointment_data:   dict           = {}   # {number: {name, contact, email, date, servicio, ...}}
processed_messages: set            = set()


# ── Estado del usuario ─────────────────────────────────────────────────────────
def set_state(user_number: str, state: str) -> None:
    """Actualiza estado y marca timestamp de interacción."""
    with state_lock:
        user_state.setdefault(user_number, {})['state']            = state
        user_state[user_number]['last_interaction'] = datetime.now()


def force_state(user_number: str, state: str) -> None:
    """Cambia estado sin actualizar last_interaction (uso interno en threads)."""
    with state_lock:
        user_state.setdefault(user_number, {})['state'] = state


def get_state(user_number: str) -> str:
    with state_lock:
        return user_state.get(user_number, {}).get('state', 'main')


def get_last_interaction(user_number: str) -> datetime:
    with state_lock:
        return user_state.get(user_number, {}).get('last_interaction', datetime.now())


def touch_interaction(user_number: str) -> None:
    with state_lock:
        if user_number in user_state:
            user_state[user_number]['last_interaction'] = datetime.now()


# ── Procesamiento (mutex para evitar double-submit) ───────────────────────────
def is_processing(user_number: str) -> bool:
    with state_lock:
        return user_state.get(user_number, {}).get('processing', False)


def set_processing(user_number: str, value: bool) -> None:
    with state_lock:
        user_state.setdefault(user_number, {})['processing'] = value


# ── Datos de la cita en curso ─────────────────────────────────────────────────
def update_appointment(user_number: str, **kwargs) -> None:
    with state_lock:
        appointment_data.setdefault(user_number, {}).update(kwargs)


def get_appointment(user_number: str) -> dict:
    with state_lock:
        return dict(appointment_data.get(user_number, {}))


def pop_appointment_keys(user_number: str, *keys: str) -> None:
    with state_lock:
        data = appointment_data.get(user_number, {})
        for k in keys:
            data.pop(k, None)


def clear_appointment_data(user_number: str) -> None:
    with state_lock:
        appointment_data.pop(user_number, None)


def get_available_slots(user_number: str) -> list:
    with state_lock:
        return list(appointment_data.get(user_number, {}).get('available_slots', []))


def clear_session(user_number: str) -> None:
    """Elimina estado y datos de cita del usuario (al finalizar flujo)."""
    with state_lock:
        user_state.pop(user_number, None)
        appointment_data.pop(user_number, None)


# ── Deduplicación de mensajes entrantes ───────────────────────────────────────
def is_duplicate_message(message_id: str) -> bool:
    """Retorna True si ya se procesó este message_id (y lo registra si es nuevo)."""
    with state_lock:
        if message_id in processed_messages:
            return True
        processed_messages.add(message_id)
        if len(processed_messages) > MAX_PROCESSED_SIZE:
            processed_messages.clear()
        return False
#buzon
web_messages: dict = {}

def queue_web_message(session_id: str, text: str, image: str = None) -> None:
    """Guarda un mensaje en el buzón del usuario web."""
    with state_lock:
        if session_id not in web_messages:
            web_messages[session_id] = []
        web_messages[session_id].append({'text': text, 'image': image})

def get_web_messages(session_id: str) -> list:
    """Saca y elimina los mensajes del buzón para enviarlos a la web."""
    with state_lock:
        msgs = web_messages.get(session_id, [])
        web_messages[session_id] = [] # Limpiamos el buzón tras leerlos
        return msgs
