# tests/conftest.py – Configuración global de pytest (env vars dummy para tests)
import os
import tempfile

# Establecer variables de entorno ANTES de que cualquier módulo del proyecto
# sea importado, para evitar ValueError en config.py
_tmp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
_tmp_db.close()

os.environ.setdefault('WHATSAPP_PHONE_ID', 'test_phone_id')
os.environ.setdefault('WHATSAPP_TOKEN',    'test_token')
os.environ.setdefault('EMAIL_SENDER',      'test@test.com')
os.environ.setdefault('EMAIL_PASSWORD',    'test_password')
os.environ.setdefault('DB_PATH',           _tmp_db.name)
