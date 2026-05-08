# tests/test_menus.py – Tests de la capa de presentación (menús)
#
# REGLA DE PATCH: parchear DONDE se usa el nombre, no donde se define.
# menus.py hace `from services.whatsapp import send_whatsapp`, por lo que
# hay que parchear 'presentation.menus.send_whatsapp' (no 'services.whatsapp.send_whatsapp').
import pytest
from unittest.mock import patch

from presentation.menus import (
    menu1, subMenu1, subMenu1_2, onePage, multiPage, appWeb,
    subMenu2, subMenu3, hablarAsesor,
    optimizaSistemaRendimiento, seguridadEliminacionMalware,
    soporteSoftApps, remoto
)
from core.state import get_state, user_state, appointment_data

USER = '573000000001'

# Alias de los targets de patch (donde menus.py usa los nombres)
_WA    = 'presentation.menus.send_whatsapp'
_EMAIL = 'presentation.menus.send_email'


@pytest.fixture(autouse=True)
def cleanup():
    yield
    user_state.pop(USER, None)
    appointment_data.pop(USER, None)


class TestMenusPrincipales:
    @pytest.mark.parametrize('fn, expected_state, fragment', [
        (menu1,      'main',        'bienvenido a proyectos web'),
        (subMenu1,   'services',    'servicios que ofrecemos'),
        (subMenu1_2, 'web_dev',     'páginas o aplicaciones web'),
        (subMenu2,   'maintenance', 'mantenimiento y software'),
        (subMenu3,   'chatbot_info','chatbot'),
    ])
    def test_menu_cambia_estado_y_envia_texto_correcto(self, fn, expected_state, fragment):
        with patch(_WA) as mock_send:
            fn(USER)
        assert get_state(USER) == expected_state
        texto_enviado = mock_send.call_args[0][1].lower()
        assert fragment in texto_enviado


class TestSubmenusDetalle:
    @pytest.mark.parametrize('fn, expected_state', [
        (onePage,                    'sub_menu_one_page'),
        (multiPage,                  'sub_menu_multi_page'),
        (appWeb,                     'sub_menu_web_app'),
        (optimizaSistemaRendimiento, 'opsisren'),
        (seguridadEliminacionMalware,'seguElimMa'),
        (soporteSoftApps,            'soprtSofApps'),
        (remoto,                     'remoto'),
    ])
    def test_submenus_detalle_establecen_estado_correcto(self, fn, expected_state):
        with patch(_WA):
            fn(USER)
        assert get_state(USER) == expected_state

    @pytest.mark.parametrize('fn', [
        onePage, multiPage, appWeb,
        optimizaSistemaRendimiento, seguridadEliminacionMalware,
        soporteSoftApps, remoto
    ])
    def test_submenus_detalle_ofrecen_opciones_hablar_y_agendar(self, fn):
        with patch(_WA) as mock_send:
            fn(USER)
        texto = mock_send.call_args[0][1].lower()
        assert '1-' in texto   # opción 1: hablar con ingeniero
        assert '2-' in texto   # opción 2: agendar cita
        assert '0-' in texto   # opción 0: volver


class TestHablarAsesor:
    def test_cambia_estado_a_start(self):
        with patch(_WA), patch(_EMAIL):
            hablarAsesor(USER, 'Chatbot para WhatsApp')
        assert get_state(USER) == 'start'

    def test_envia_email_al_ingeniero_con_servicio(self):
        with patch(_WA), patch(_EMAIL) as mock_email:
            hablarAsesor(USER, 'Chatbot para WhatsApp')
        assert mock_email.called
        body = mock_email.call_args[0][2]
        assert 'Chatbot para WhatsApp' in body
        assert USER in body

    def test_envia_email_sin_servicio_especificado(self):
        with patch(_WA), patch(_EMAIL) as mock_email:
            hablarAsesor(USER)
        assert mock_email.called
        body = mock_email.call_args[0][2]
        assert 'No especificó' in body

    def test_asunto_del_email_incluye_servicio(self):
        with patch(_WA), patch(_EMAIL) as mock_email:
            hablarAsesor(USER, 'Aplicación Web')
        subject = mock_email.call_args[0][1]
        assert 'Aplicación Web' in subject

    def test_mensaje_whatsapp_incluye_numero_ingeniero(self):
        with patch(_WA) as mock_wa, patch(_EMAIL):
            hablarAsesor(USER)
        texto = mock_wa.call_args[0][1]
        assert '310 7791984' in texto
