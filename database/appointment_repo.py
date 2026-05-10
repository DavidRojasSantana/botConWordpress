# database/appointment_repo.py – Capa de acceso a datos (MongoDB)
from pymongo import MongoClient
import os
from config import MONGO_URI
from models.appointment import Appointment

# Cliente global
_client = None
_db = None

def init_db() -> None:
    """Inicializa la conexión con MongoDB."""
    global _client, _db
    try:
        # Si no hay URI en config, no conectamos, pero podemos advertir
        if not MONGO_URI:
            print("Advertencia: No se encontró MONGO_URI en la configuración.")
            return

        _client = MongoClient(MONGO_URI)

        # Intentamos obtener la base de datos por defecto del URI
        try:
            from pymongo.errors import ConfigurationError
            _db = _client.get_default_database()
        except ConfigurationError:
            # Si el URI no tiene una base de datos definida al final, usamos una por defecto
            _db = _client.get_database('fundacion_julian')

        # Test de conexión
        _client.admin.command('ping')
        print(f"Conectado a MongoDB, base de datos: {_db.name}")
    except Exception as e:
        print(f"Error inicializando MongoDB: {e}")


def save_appointment(appt: Appointment) -> None:
    """Inserta una cita confirmada en la base de datos MongoDB."""
    global _db
    if _db is None:
        print("Error: Base de datos no inicializada.")
        return

    try:
        # Convertimos el dataclass a dict, omitiendo los id temporales si es necesario
        from dataclasses import asdict
        doc = asdict(appt)

        if doc.get('id') is None:
            del doc['id'] # MongoDB usará _id

        result = _db.appointments.insert_one(doc)
        print(f"Cita guardada en MongoDB con _id: {result.inserted_id}")
    except Exception as e:
        print(f"Error guardando cita en MongoDB: {e}")


def get_all_appointments() -> list:
    """Retorna todas las citas guardadas."""
    global _db
    if _db is None:
        return []

    try:
        # Buscamos todas y ordenamos por fecha (si tiene un formato ordenable, YYYY-MM-DD HH:MM)
        cursor = _db.appointments.find().sort("appointment_date", 1)
        results = []
        for doc in cursor:
            # Convertimos ObjectId a string por si se requiere enviar por JSON
            doc['_id'] = str(doc['_id'])
            results.append(doc)
        return results
    except Exception as e:
        print(f"Error leyendo citas de MongoDB: {e}")
        return []
