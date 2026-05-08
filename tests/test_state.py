# tests/test_state.py – Tests de la capa de gestión de estado
import pytest
from core.state import (
    set_state, get_state, force_state,
    update_appointment, get_appointment, clear_appointment_data,
    clear_session, is_processing, set_processing,
    pop_appointment_keys, get_available_slots,
    is_duplicate_message,
    user_state, appointment_data, processed_messages
)

USER = '573001234567'


@pytest.fixture(autouse=True)
def cleanup():
    yield
    user_state.pop(USER, None)
    appointment_data.pop(USER, None)
    processed_messages.clear()


class TestEstadoUsuario:
    def test_estado_por_defecto_es_main(self):
        assert get_state('numero_inexistente_xyz') == 'main'

    def test_set_y_get_state(self):
        set_state(USER, 'services')
        assert get_state(USER) == 'services'

    def test_force_state_no_actualiza_last_interaction(self):
        set_state(USER, 'main')
        ts_antes = user_state[USER].get('last_interaction')
        force_state(USER, 'awaiting_name')
        assert get_state(USER) == 'awaiting_name'
        assert user_state[USER].get('last_interaction') == ts_antes


class TestDatosDeCita:
    def test_update_y_get_appointment(self):
        update_appointment(USER, name='Prueba', email='p@p.com')
        data = get_appointment(USER)
        assert data['name'] == 'Prueba'
        assert data['email'] == 'p@p.com'

    def test_update_no_sobreescribe_campos_previos(self):
        update_appointment(USER, name='Ana')
        update_appointment(USER, email='ana@e.com')
        data = get_appointment(USER)
        assert data['name'] == 'Ana'
        assert data['email'] == 'ana@e.com'

    def test_pop_appointment_keys(self):
        update_appointment(USER, date_str='25/09/2026', available_slots=['09:00'])
        pop_appointment_keys(USER, 'date_str', 'available_slots')
        data = get_appointment(USER)
        assert 'date_str' not in data
        assert 'available_slots' not in data

    def test_get_available_slots(self):
        update_appointment(USER, available_slots=['08:00', '10:00', '14:00'])
        assert get_available_slots(USER) == ['08:00', '10:00', '14:00']

    def test_get_available_slots_sin_datos(self):
        assert get_available_slots(USER) == []

    def test_clear_appointment_data(self):
        update_appointment(USER, name='Test')
        clear_appointment_data(USER)
        assert get_appointment(USER) == {}


class TestProcessing:
    def test_processing_false_por_defecto(self):
        assert is_processing(USER) is False

    def test_set_y_get_processing(self):
        set_processing(USER, True)
        assert is_processing(USER) is True
        set_processing(USER, False)
        assert is_processing(USER) is False


class TestClearSession:
    def test_clear_session_elimina_estado_y_datos(self):
        set_state(USER, 'services')
        update_appointment(USER, name='Test')
        clear_session(USER)
        assert get_state(USER) == 'main'
        assert get_appointment(USER) == {}


class TestDeduplicacion:
    def test_primer_mensaje_no_es_duplicado(self):
        assert is_duplicate_message('msg_001') is False

    def test_mismo_mensaje_es_duplicado(self):
        is_duplicate_message('msg_002')
        assert is_duplicate_message('msg_002') is True

    def test_mensajes_distintos_no_son_duplicados(self):
        assert is_duplicate_message('msg_003') is False
        assert is_duplicate_message('msg_004') is False
