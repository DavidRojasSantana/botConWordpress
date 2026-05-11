# core/bot.py – Máquina de estados: decide qué hacer con cada mensaje entrante
import threading

from config import SALUDOS
from services.whatsapp import send_telegram
import core.state as state
from core.appointment_flow import consultaHorariosDisponibles, verificaDisponibilidad
from core.questionnaire import QUESTIONS, evaluate_questionnaire

# Importación diferida para evitar ciclos (presentation → core → presentation)
def _menus():
    from presentation import menus
    return menus


def handle_message(user_number: str, user_text_raw: str) -> None:
    """Punto de entrada del bot: enruta cada mensaje a la acción correcta."""
    user_text     = user_text_raw.lower()
    current_state = state.get_state(user_number)
    m             = _menus()   # acceso perezoso a los menús

    # Si estamos en preguntas (q0, q1, ..., q39)
    if current_state.startswith('q'):
        try:
            q_idx = int(current_state[1:])
        except ValueError:
            q_idx = -1

        if 0 <= q_idx < len(QUESTIONS):
            # Guardar la respuesta
            appt_data = state.get_appointment(user_number)
            answers = appt_data.get('respuestas', [])

            # Solo permitir "si" o "no"
            if user_text not in ['si', 'sí', 's', 'no', 'n']:
                send_telegram(user_number, 'Por favor responde únicamente "Sí" o "No".')
                return

            # Agregar la respuesta a la lista y actualizar
            if len(answers) <= q_idx:
                answers.append(user_text_raw)
            else:
                answers[q_idx] = user_text_raw
            state.update_appointment(user_number, respuestas=answers)

            # Pasar a la siguiente pregunta
            next_idx = q_idx + 1
            if next_idx < len(QUESTIONS):
                send_telegram(user_number, f"Pregunta {next_idx + 1}/40:\n{QUESTIONS[next_idx][0]}")
                state.force_state(user_number, f'q{next_idx}')
            else:
                # Terminamos las preguntas. Evaluar!
                send_telegram(user_number, 'Gracias por completar el cuestionario. Estamos evaluando tus respuestas...')
                especialidad = evaluate_questionnaire(answers)
                state.update_appointment(user_number, especialidad=especialidad)

                send_telegram(
                    user_number,
                    f'Según tus respuestas, te recomendamos agendar con: *{especialidad}*.\n\n'
                    'Por favor, dime la fecha para la cita en formato dd/mm/aaaa\n'
                    '(Ej: 25/09/2026)'
                )
                state.force_state(user_number, 'awaiting_date')
        return

    match (current_state, user_text):

        case ('awaiting_timeslot', '0'):
            # Volver a pedir fecha
            state.pop_appointment_keys(user_number, 'available_slots', 'date_str')
            send_telegram(
                user_number,
                'Escribe la fecha para la cita en formato dd/mm/aaaa por favor\n'
                '(Ej: 25/09/2026)\n\n'
                'Escribe 0 para cancelar y volver al menú principal.'
            )
            state.force_state(user_number, 'awaiting_date')

        case (st, '0') if st in ('awaiting_tutor', 'awaiting_child', 'awaiting_contact', 'awaiting_email', 'awaiting_grade', 'awaiting_age', 'awaiting_date'):
            state.clear_appointment_data(user_number)
            m.menu1(user_number)

        # ── b) CAPTURA DE DATOS ────────────────────────────────────────────────

        case ('awaiting_tutor', _):
            if not user_text_raw:
                send_telegram(user_number, 'Por favor envía tu nombre (tutor) como texto.')
            else:
                state.update_appointment(user_number, nombre_tutor=user_text_raw)
                send_telegram(user_number, 'Gracias. Ahora dime el nombre del niño/a.')
                state.force_state(user_number, 'awaiting_child')

        case ('awaiting_child', _):
            if not user_text_raw:
                send_telegram(user_number, 'Por favor envía el nombre del niño/a como texto.')
            else:
                state.update_appointment(user_number, nombre_nino=user_text_raw)
                send_telegram(user_number, 'Perfecto. Dime tu número de celular de contacto (ej: +57 3XX...).')
                state.force_state(user_number, 'awaiting_contact')

        case ('awaiting_contact', _):
            if not user_text_raw:
                send_telegram(user_number, 'Por favor envía el celular de contacto como texto.')
            else:
                state.update_appointment(user_number, celular_contacto=user_text_raw)
                send_telegram(user_number, 'Muy bien. Por favor escribe tu correo electrónico.')
                state.force_state(user_number, 'awaiting_email')

        case ('awaiting_email', _):
            if not user_text_raw:
                send_telegram(user_number, 'Por favor envía tu correo electrónico como texto.')
            else:
                state.update_appointment(user_number, email=user_text_raw)
                send_telegram(user_number, 'Ahora, indícame en qué grado escolar se encuentra el niño/a.')
                state.force_state(user_number, 'awaiting_grade')

        case ('awaiting_grade', _):
            if not user_text_raw:
                send_telegram(user_number, 'Por favor envía el grado escolar como texto.')
            else:
                state.update_appointment(user_number, grado_escolar=user_text_raw)
                send_telegram(user_number, 'Gracias. ¿Qué edad tiene el niño/a?')
                state.force_state(user_number, 'awaiting_age')

        case ('awaiting_age', _):
            if not user_text_raw:
                send_telegram(user_number, 'Por favor envía la edad como texto.')
            else:
                state.update_appointment(user_number, edad=user_text_raw, respuestas=[])
                send_telegram(
                    user_number,
                    'Excelente. A continuación te haré 40 preguntas para evaluar las necesidades del niño/a.\n'
                    'Por favor, responde a cada una únicamente con "Sí" o "No".\n\n'
                    f'Pregunta 1/40:\n{QUESTIONS[0][0]}'
                )
                state.force_state(user_number, 'q0')

        case ('awaiting_date', _):
            if not user_text_raw:
                send_telegram(user_number, 'Por favor envía la fecha como texto (Ej: 25/09/2026).')
            else:
                if state.is_processing(user_number):
                    send_telegram(user_number, 'Consultando horarios disponibles, espera un momento...')
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
                send_telegram(user_number, 'Por favor escribe solo el número de la opción.')
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
                        send_telegram(user_number, 'Estamos procesando tu solicitud. Por favor espera...')
                    else:
                        state.set_processing(user_number, True)
                        threading.Thread(
                            target=verificaDisponibilidad,
                            args=(user_number,
                                  appt_data.get('nombre_tutor'),
                                  appt_data.get('celular_contacto'),
                                  appt_data.get('email'),
                                  datetime_str),
                            daemon=True
                        ).start()

        # ── c) NAVEGACIÓN PRINCIPAL ───────────────────────────────────────────

        case (st, txt) if txt in SALUDOS and st in ('main', 'start'):
            m.menu1(user_number)

        case ('main', '1'):
            send_telegram(user_number, '¡Excelente! Para iniciar, por favor dime tu nombre (nombre del tutor).')
            state.force_state(user_number, 'awaiting_tutor')

        case _:
            send_telegram(
                user_number,
                'Lo siento, no entiendo tu solicitud. '
                'Escribe "hola" para reiniciar el bot.'
            )
            state.force_state(user_number, 'main')
