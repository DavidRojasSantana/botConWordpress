# core/appointment_flow.py – Lógica de negocio: consulta de horarios y agendamiento
import threading
from datetime import datetime, timedelta

# ── Lock por franja horaria (evita doble reserva simultánea) ──────────────────
# Problema sin esto: dos hilos hacen is_available() al mismo tiempo -> ambos True
# -> ambos llaman create_event() -> doble reserva en el mismo slot.
# Solución: lock por slot garantiza que check + create sean atómicos.
_slot_locks: dict            = {}
_slot_locks_guard: threading.Lock = threading.Lock()


def _get_slot_lock(slot_key: str) -> threading.Lock:
    """Retorna (crea si no existe) el lock exclusivo para una franja horaria."""
    with _slot_locks_guard:
        if slot_key not in _slot_locks:
            _slot_locks[slot_key] = threading.Lock()
        return _slot_locks[slot_key]

from config import HORARIOS, CALENDAR_ID, ENGINEER_EMAIL, EMAIL_SENDER
from models.appointment import Appointment
from database.appointment_repo import save_appointment
from services.whatsapp import send_telegram
from services.email import send_email
from services.calendar import GoogleCalendarManager
import core.state as state


def consultaHorariosDisponibles(user_number: str, date_str: str) -> None:
   
    try:
        # Validar formato de fecha
        try:
            fecha = datetime.strptime(date_str.strip(), '%d/%m/%Y')
        except ValueError:
            send_telegram(
                user_number,
                'No pude entender la fecha. Usa el formato dd/mm/aaaa\n'
                '(Ej: 25/09/2026)'
            )
            state.force_state(user_number, 'awaiting_date')
            return

        # No permitir fechas pasadas
        if fecha.date() < datetime.now().date():
            send_telegram(user_number,
                          'Esa fecha ya pasó. Por favor elige una fecha futura.')
            state.force_state(user_number, 'awaiting_date')
            return

        # Autenticar Google Calendar
        try:
            cal = GoogleCalendarManager(calendar_id=CALENDAR_ID)
            cal.authenticate()
        except Exception as e:
            send_telegram(user_number,
                          'Error con Google Calendar. Contacta soporte.')
            print(f"[calendar] error de autenticación: {e}")
            return

        # Verificar cada franja horaria del día
        disponibles = []
        for hora in HORARIOS:
            h, m  = map(int, hora.split(':'))
            start = fecha.replace(hour=h, minute=m, second=0, microsecond=0)
            end   = start + timedelta(hours=1)
            if cal.is_available(start, end):
                disponibles.append(hora)

        # Sin disponibilidad ese día
        if not disponibles:
            send_telegram(
                user_number,
                f'Lo sentimos, no hay horarios disponibles para el {date_str.strip()}.\n\n'
                'Escribe otra fecha (Ej: 26/09/2026)\n'
                'o escribe 0 para volver al menú principal.'
            )
            state.force_state(user_number, 'awaiting_date')
            return

        # Guardar slots disponibles y fecha en appointment_data
        state.update_appointment(user_number,
                                 date_str=date_str.strip(),
                                 available_slots=disponibles)

        # Construir y enviar menú numerado
        lineas = [f'Tenemos agenda para el {date_str.strip()}.\nSelecciona una hora:\n']
        for i, hora in enumerate(disponibles, 1):
            lineas.append(f'{i}- {hora}')
        lineas.append('\n0- Elegir otra fecha')
        send_telegram(user_number, '\n'.join(lineas))

        state.force_state(user_number, 'awaiting_timeslot')
        state.touch_interaction(user_number)

    except Exception as e:
        print(f"[consultaHorariosDisponibles] error: {e}")
        send_telegram(user_number,
                      'Error consultando horarios. Intenta más tarde.')
    finally:
        state.set_processing(user_number, False)

def verificaDisponibilidad(user_number: str, name: str, contact_number: str,
                           email: str, date_text: str) -> None:
   
    try:
        # Parsear fecha + hora
        try:
            start_time = datetime.strptime(date_text, '%d/%m/%Y %H:%M')
        except ValueError:
            send_telegram(
                user_number,
                'Lo siento, no pude entender la fecha. '
                'Usa el formato: dd/mm/aaaa hh:mm (Ej: 25/09/2026 10:00).'
            )
            state.force_state(user_number, 'awaiting_date')
            return

        end_time = start_time + timedelta(hours=1)

        # Autenticar Google Calendar
        try:
            cal = GoogleCalendarManager(calendar_id=CALENDAR_ID)
            cal.authenticate()
        except Exception as e:
            send_telegrams(user_number,
                          'Error con Google Calendar. Contacta soporte.')
            print(f"[calendar] error de autenticación: {e}")
            return

        # ── SECCIÓN CRÍTICA: lock por slot (TOCTOU fix) ───────────────────────
        # Garantiza que is_available() y create_event() sean atómicos para
        # este slot, impidiendo que dos usuarios reserven el mismo horario.
        slot_key  = start_time.strftime('%Y-%m-%d %H:%M')
        slot_lock = _get_slot_lock(slot_key)

        adquirido = slot_lock.acquire(timeout=15)
        if not adquirido:
            print(f"[slot] Timeout adquiriendo lock para {slot_key}", flush=True)
            send_telegram(
                user_number,
                'El sistema está procesando otra solicitud para ese horario. '
                'Intenta de nuevo en unos segundos.'
            )
            return

        confirmacion_texto = None
        try:
            # Re-verificar dentro del lock (ahora es seguro)
            if not cal.is_available(start_time, end_time):
                send_telegram(
                    user_number,
                    'Lo siento, ese horario acaba de ser reservado por otra persona. '
                    'Por favor elige otra fecha u hora.'
                )
                state.force_state(user_number, 'awaiting_date')
                return

            fecha_hora = start_time.strftime('%d/%m/%Y %H:%M')

            # Crear evento en Google Calendar (envía invitación al cliente)
            cal.create_event(name, contact_number, email, start_time, end_time, '')

            # Guardar en MongoDB
            save_appointment(Appointment(
                name=name,
                contact_number=contact_number,
                email=email,
                appointment_date=start_time.strftime('%Y-%m-%d %H:%M')
            ))

            print(f"[cita] [OK] Slot {slot_key} reservado para {name}", flush=True)

            # Preparar texto de confirmación (se enviará FUERA del lock)
            confirmacion_texto = (
                f'✅ ¡Cita agendada con éxito en la Fundación de Julián!\n\n'
                f'👤 Nombre: {name}\n'
                f'📅 Fecha y hora: {fecha_hora}\n'
                f'📞 Contacto: {contact_number}\n'
                f'📧 Correo: {email}\n'
                'Recibirás una invitación en tu correo con los detalles.\n\n'
                'Escribe "hola" para volver al menú principal.'
            )

        finally:
            slot_lock.release()   # Liberar SIEMPRE, incluso si hay excepción
        # ── FIN SECCIÓN CRÍTICA ────────────────────────────────────────────────

        # Las notificaciones van FUERA del lock (no bloquean otros usuarios)
        if confirmacion_texto:
            send_telegram(user_number, confirmacion_texto)

            dest = ENGINEER_EMAIL or EMAIL_SENDER
            print(f"[cita] Notificando a la fundación -> {dest}", flush=True)
            ok = send_email(
                dest,
                f'Nueva cita agendada – {name} – {fecha_hora}',
                f'Hola,\n\n'
                f'Se agendó una nueva cita desde el chatbot de WhatsApp para la Fundación de Julián.\n\n'
                f'👤 Nombre: {name}\n'
                f'📱 WhatsApp de origen: +{user_number}\n'
                f'📧 Correo: {email}\n'
                f'📞 Contacto: {contact_number}\n'
                f'📅 Fecha y hora: {fecha_hora}\n\n'
                f'El evento ya fue creado en Google Calendar y el cliente recibió la invitación.\n\n'
                f'— Chatbot Fundación de Julián'
            )
            print(f"[cita] Email a la fundación: {'OK enviado' if ok else 'FALLO'}", flush=True)

        # Limpiar sesión del usuario
        state.clear_session(user_number)

    except Exception as e:
        print(f"[verificaDisponibilidad] error: {e}")
        send_telegram(
            user_number,
            'Ocurrió un error interno al agendar tu cita. '
            'Por favor intenta más tarde.'
        )
    finally:
        state.set_processing(user_number, False)
