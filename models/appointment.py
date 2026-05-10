# models/appointment.py – Modelo de datos de una cita
from dataclasses import dataclass, field


@dataclass
class Appointment:
    """Representa una cita agendada a través del chatbot de Fundación de Julián."""
    nombre_nino:      str
    nombre_tutor:     str
    celular_contacto: str
    email:            str
    grado_escolar:    str
    edad:             str
    appointment_date: str        # formato 'YYYY-MM-DD HH:MM'
    especialidad:     str = ''   # especialidad recomendada tras cuestionario
    respuestas:       list = field(default_factory=list) # respuestas del cuestionario
    id:               int = None
    created_at:       str = ''
