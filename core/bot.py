# core/bot.py – Máquina de estados: decide qué hacer con cada mensaje entrante
import threading

from config import DETAIL_STATES, AWAITING_STATES, SERVICE_LABELS, SALUDOS
from services.whatsapp import send_telegram
import core.state as state
from core.appointment_flow import consultaHorariosDisponibles, verificaDisponibilidad

# Importación diferida para evitar ciclos (presentation → core → presentation)
def _menus():
    from presentation import menus
    return menus


def handle_message(user_number: str, user_text_raw: str) -> None:
    """Punto de entrada del bot: enruta cada mensaje a la acción correcta."""
    user_text     = user_text_raw.lower()
    current_state = state.get_state(user_number)
    m             = _menus()   # acceso perezoso a los menús

    match (current_state, user_text):

        # ── a) BACK desde flujo de cita (DEBE ir antes del wildcard) ──────────

        case ('awaiting_timeslot', '0'):
            # Volver a pedir fecha sin borrar el servicio de interés ya guardado
            state.pop_appointment_keys(user_number, 'available_slots', 'date_str')
            send_telegram(
                user_number,
                'Escribe la fecha para la cita en formato dd/mm/aaaa por favor\n'
                '(Ej: 25/09/2026)\n\n'
                'Escribe 0 para volver al menú principal.'
            )
            state.force_state(user_number, 'awaiting_date')

        case (st, '0') if st in AWAITING_STATES:
            state.clear_appointment_data(user_number)
            m.menu1(user_number)

        # ── b) CAPTURA DE DATOS DE CITA (wildcards) ───────────────────────────

        case ('awaiting_name', _):
            if not user_text_raw:
                send_telegram(user_number,
                              'Por favor envía tu nombre completo como en formato texto no audios ni imagenes')
            else:
                state.update_appointment(user_number, name=user_text_raw)
                send_telegram(user_number,
                              'Gracias. Ahora dime tu número de contacto (ej: +57 3XX...).')
                state.force_state(user_number, 'awaiting_contact')

        case ('awaiting_contact', _):
            if not user_text_raw:
                send_telegram(user_number,
                              'Por favor envía tu número de contacto como texto.')
            else:
                state.update_appointment(user_number, contact_number=user_text_raw)
                send_telegram(user_number,
                              'Perfecto. Por favor escribe tu correo electrónico.')
                state.force_state(user_number, 'awaiting_email')

        case ('awaiting_email', _):
            if not user_text_raw:
                send_telegram(user_number,
                              'Por favor envía tu correo electrónico como texto.')
            else:
                state.update_appointment(user_number, email=user_text_raw)
                send_telegram(
                    user_number,
                    'Perfecto. Ahora dime la fecha para la cita en formato dd/mm/aaaa\n'
                    '(Ej: 25/09/2026)\n\n'
                    'Escribe 0 para volver al menú principal.'
                )
                state.force_state(user_number, 'awaiting_date')

        case ('awaiting_date', _):
            if not user_text_raw:
                send_telegram(user_number,
                              'Por favor envía la fecha como texto (Ej: 25/09/2026).')
            else:
                if state.is_processing(user_number):
                    send_telegram(user_number,
                                  'Consultando horarios disponibles, espera un momento...')
                else:
                    state.set_processing(user_number, True)
                    threading.Thread(
                        target=consultaHorariosDisponibles,
                        args=(user_number, user_text_raw),
                        daemon=True
                    ).start()

        case ('awaiting_timeslot', _):
            slots = state.get_available_slots(user_number)
            if not user_text_raw.isdigit():
                send_telegram(user_number,
                              'Por favor escribe solo el número de la opción.')
            else:
                idx = int(user_text_raw)
                if idx < 1 or idx > len(slots):
                    send_telegram(
                        user_number,
                        f'Opción no válida. Elige un número entre 1 y {len(slots)},\n'
                        'o escribe 0 para elegir otra fecha.'
                    )
                else:
                    hora_elegida = slots[idx - 1]
                    appt_data    = state.get_appointment(user_number)
                    date_str     = appt_data.get('date_str', '')
                    datetime_str = f"{date_str} {hora_elegida}"

                    if state.is_processing(user_number):
                        send_telegram(user_number,
                                      'Estamos procesando tu solicitud. Por favor espera...')
                    else:
                        state.set_processing(user_number, True)
                        threading.Thread(
                            target=verificaDisponibilidad,
                            args=(user_number,
                                  appt_data.get('name'),
                                  appt_data.get('contact_number'),
                                  appt_data.get('email'),
                                  datetime_str),
                            daemon=True
                        ).start()

        # ── c) NAVEGACIÓN DE MENÚS ────────────────────────────────────────────

        case (st, txt) if txt in SALUDOS and st in ('main', 'start'):
            m.menu1(user_number)

        case ('main', '1'):
            send_telegram(user_number, '¡Excelente! Para agendar tu cita, por favor dime tu nombre completo.')
            state.force_state(user_number, 'awaiting_name')

        case _:
            send_telegram(
                user_number,
                'Lo siento, no entiendo tu solicitud. '
                'Escribe "hola" para reiniciar el bot.'
            )
            state.force_state(user_number, 'main')
