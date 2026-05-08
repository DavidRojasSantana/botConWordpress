# services/whatsapp.py – Wrapper de la API de WhatsApp Business

import core.state as state

def send_telegram(to: str, text: str, image: str = None) -> dict:
    """
    Simula el envío de Telegram/WhatsApp, pero en su lugar 
    guarda el mensaje en el buzón web de Coldima.
    (Mantenemos el nombre de la función para no romper otras partes del código).
    """
    # Usamos la función que ya agregaste en core/state.py
    state.queue_web_message(to, text, image)
    
    return {'status': 'queued in web backend'}