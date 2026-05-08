# tests/test_appointment_repo.py – Tests de la capa de base de datos
import os
import sqlite3
import pytest

from models.appointment import Appointment
from database.appointment_repo import init_db, save_appointment, get_all_appointments
from config import DB_PATH


@pytest.fixture(autouse=True)
def clean_db():
    """Limpia la tabla antes de cada test."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM appointments')
    conn.commit()
    conn.close()
    yield


class TestSaveAppointment:
    def test_guarda_cita_completa(self):
        appt = Appointment(
            name='Ana García',
            contact_number='+573001234567',
            email='ana@example.com',
            appointment_date='2026-05-10 10:00',
            servicio='Páginas One Page'
        )
        save_appointment(appt)
        citas = get_all_appointments()
        assert len(citas) == 1
        assert citas[0]['name'] == 'Ana García'
        assert citas[0]['servicio'] == 'Páginas One Page'
        assert citas[0]['email'] == 'ana@example.com'

    def test_guarda_cita_sin_servicio(self):
        appt = Appointment(
            name='Luis Pérez',
            contact_number='+573009876543',
            email='luis@example.com',
            appointment_date='2026-05-11 14:00'
        )
        save_appointment(appt)
        citas = get_all_appointments()
        assert citas[0]['servicio'] == ''

    def test_multiples_citas_ordenadas_por_fecha(self):
        for date, name in [('2026-05-15 09:00', 'Carlos'),
                           ('2026-05-10 08:00', 'María')]:
            save_appointment(Appointment(
                name=name, contact_number='+57300',
                email='x@x.com', appointment_date=date
            ))
        citas = get_all_appointments()
        assert citas[0]['name'] == 'María'    # fecha menor primero
        assert citas[1]['name'] == 'Carlos'


class TestGetAllAppointments:
    def test_retorna_lista_vacia_sin_citas(self):
        assert get_all_appointments() == []

    def test_retorna_todas_las_citas(self):
        for i in range(3):
            save_appointment(Appointment(
                name=f'Cliente {i}', contact_number=f'+5730{i}',
                email=f'c{i}@e.com',
                appointment_date=f'2026-06-0{i+1} 10:00'
            ))
        assert len(get_all_appointments()) == 3
