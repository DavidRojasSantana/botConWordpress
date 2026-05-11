# models/appointment.py – Modelo de datos de una cita
from dataclasses import dataclass, field


@dataclass
class Appointment:
    """Representa una cita agendada a través del chatbot."""
    name:             str
    contact_number:   str
    email:            str
    appointment_date: str
    id:               int = None
    created_at:       str = ''
