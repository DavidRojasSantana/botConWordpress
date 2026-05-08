# database/appointment_repo.py – Capa de acceso a datos (SQLite)
import sqlite3
from config import DB_PATH
from models.appointment import Appointment


def init_db() -> None:
    """Crea la tabla de citas si no existe y migra columnas nuevas."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT    NOT NULL,
            contact_number   TEXT    NOT NULL,
            email            TEXT,
            servicio         TEXT    DEFAULT '',
            appointment_date TEXT    NOT NULL,
            created_at       TEXT    DEFAULT (datetime('now','localtime'))
        )
    ''')
    # Compatibilidad con bases de datos existentes sin la columna 'servicio'
    try:
        conn.execute("ALTER TABLE appointments ADD COLUMN servicio TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass  # columna ya existe
    conn.commit()
    conn.close()
    print(f"Base de datos lista: {DB_PATH}")


def save_appointment(appt: Appointment) -> None:
    """Inserta una cita confirmada en la base de datos."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            'INSERT INTO appointments '
            '(name, contact_number, email, servicio, appointment_date) '
            'VALUES (?, ?, ?, ?, ?)',
            (appt.name, appt.contact_number, appt.email,
             appt.servicio, appt.appointment_date)
        )
        conn.commit()
        conn.close()
        print(f"Cita guardada: {appt.name} – {appt.appointment_date} "
              f"– {appt.servicio or 'sin servicio especificado'}")
    except Exception as e:
        print(f"Error guardando cita: {e}")


def get_all_appointments() -> list:
    """Retorna todas las citas guardadas ordenadas por fecha ascendente."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            'SELECT * FROM appointments ORDER BY appointment_date ASC'
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"Error leyendo citas: {e}")
        return []
