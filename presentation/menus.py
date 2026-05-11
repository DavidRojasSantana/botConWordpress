# presentation/menus.py – Constructores de mensajes y menús del chatbot
from config import ENGINEER_EMAIL, EMAIL_SENDER

from services.whatsapp import send_telegram
import core.state as state

def menu1(user_number: str) -> None:
    texto = (
        'Bienvenido/a a la Fundación de Julián.\n\n'
        'Este es nuestro asistente virtual diseñado para ayudarte a agendar una cita.\n'
        'Para comenzar con el proceso, responde con "1".'
    )
    imagen = 'https://raw.githubusercontent.com/DavidRojasSantana/imagenes/refs/heads/main/logo1.jpg'
    send_telegram(user_number, texto, imagen)
    state.set_state(user_number, 'main')
