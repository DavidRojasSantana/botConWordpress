from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from config import ADMIN_KEY, SESSION_TIMEOUT_MINUTES
from database.appointment_repo import get_all_appointments

from services.whatsapp import send_telegram 
from presentation.menus import menu1
import core.state as state
from core.bot import handle_message

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/')
def index():
    return 'Servidor del Chatbot Web encendido y funcionando correctamente', 200

# ── NUEVAS RUTAS EXCLUSIVAS PARA WORDPRESS ──

@webhook_bp.route('/web-chat/send', methods=['POST'])
def web_chat_send():
    """Recibe los mensajes que el usuario escribe en la página web."""
    data = request.get_json(silent=True) or {}
    
    # En la web no hay número de teléfono, usamos el session_id
    session_id = data.get('session_id') 
    user_text_raw = data.get('text', '').strip()
    
    if not session_id or not user_text_raw:
        return jsonify({'error': 'Faltan datos'}), 400

    # 1. Expiración de sesión por inactividad
    last = state.get_last_interaction(session_id)
    if (datetime.now() - last) > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        send_telegram(session_id, 'La sesión ha expirado por inactividad. ¡Bienvenido de nuevo!')
        menu1(session_id)
        return jsonify({'status': 'ok'}), 200

    # 2. Delegar a la máquina de estados (tu lógica de IA y reglas)
    handle_message(session_id, user_text_raw)

    # 3. Actualizar timestamp de última interacción
    state.touch_interaction(session_id)

    return jsonify({'status': 'procesando'}), 200

@webhook_bp.route('/web-chat/poll', methods=['GET'])
def web_chat_poll():
    """El widget de la web pregunta aquí constantemente si el bot ya respondió."""
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'Falta session_id'}), 400
        
    mensajes = state.get_web_messages(session_id)
    return jsonify({'messages': mensajes}), 200

# ── RUTA ADMINISTRATIVA (Intacta) ──

@webhook_bp.route('/citas', methods=['GET'])
def ver_citas():
    if request.args.get('key', '') != ADMIN_KEY:
        return jsonify({'error': 'No autorizado'}), 403
    citas = get_all_appointments()
    return jsonify({'total': len(citas), 'citas': citas}), 200