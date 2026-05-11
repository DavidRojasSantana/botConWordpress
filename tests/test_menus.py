# tests/test_menus.py
import pytest
from unittest.mock import patch

from presentation.menus import menu1
from core.state import get_state, user_state, appointment_data

USER = '573000000001'

_WA    = 'presentation.menus.send_telegram'

@pytest.fixture(autouse=True)
def cleanup():
    yield
    user_state.pop(USER, None)
    appointment_data.pop(USER, None)

class TestMenusPrincipales:
    @pytest.mark.parametrize('fn, expected_state, fragment', [
        (menu1,      'main',        'fundación de julián'),
    ])
    def test_menu_cambia_estado_y_envia_texto_correcto(self, fn, expected_state, fragment):
        with patch(_WA) as mock_send:
            fn(USER)
        assert get_state(USER) == expected_state
        texto_enviado = mock_send.call_args[0][1].lower()
        assert fragment in texto_enviado
