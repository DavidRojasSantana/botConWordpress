# tests/test_appointment_repo.py
import pytest
from unittest.mock import patch, MagicMock

from models.appointment import Appointment
from database.appointment_repo import init_db, save_appointment, get_all_appointments
import database.appointment_repo as repo

@pytest.fixture(autouse=True)
def mock_mongo():
    with patch('database.appointment_repo.MongoClient') as mock_client:
        mock_db = MagicMock()
        mock_collection = MagicMock()

        mock_client.return_value.get_database.return_value = mock_db
        mock_client.return_value.get_default_database.return_value = mock_db
        mock_db.appointments = mock_collection

        # Simular una DB en memoria simple para el insert y find
        in_memory_db = []

        def mock_insert_one(doc):
            doc['_id'] = 'mock_id'
            in_memory_db.append(doc.copy())
            return MagicMock(inserted_id='mock_id')

        def mock_find():
            class MockCursor:
                def sort(self, *args, **kwargs):
                    return in_memory_db
            return MockCursor()

        mock_collection.insert_one.side_effect = mock_insert_one
        mock_collection.find.side_effect = mock_find

        # Forzar MONGO_URI para que pase la validación
        with patch('database.appointment_repo.MONGO_URI', 'mongodb://mock'):
            init_db()
            yield mock_collection


class TestSaveAppointment:
    def test_guarda_cita_completa(self):
        appt = Appointment(
            name='Ana García',
            contact_number='+573001234567',
            email='ana@example.com',
            appointment_date='2026-05-10 10:00'
        )
        save_appointment(appt)
        citas = get_all_appointments()
        assert len(citas) == 1
        assert citas[0]['name'] == 'Ana García'
        assert citas[0]['email'] == 'ana@example.com'


class TestGetAllAppointments:
    def test_retorna_lista_vacia_sin_citas(self):
        assert get_all_appointments() == []
