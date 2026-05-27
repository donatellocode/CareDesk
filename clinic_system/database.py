"""Database layer for Clinic Management System."""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path(__file__).parent / "clinic.db"
        self.db_path = str(db_path)
        self._init_db()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute(self, query: str, params: tuple = ()):
        """Execute a query and return affected rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid

    def execute_many(self, query: str, params: list):
        """Execute a query with multiple parameter sets."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params)
            return cursor.rowcount

    def fetch_one(self, query: str, params: tuple = ()):
        """Fetch a single row."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def _init_db(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Patients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    phone TEXT,
                    gender TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Appointments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    status TEXT DEFAULT 'waiting',
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            """)

            # Visits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    appointment_id INTEGER,
                    diagnosis TEXT,
                    notes TEXT,
                    date TEXT NOT NULL,
                    FOREIGN KEY (patient_id) REFERENCES patients (id),
                    FOREIGN KEY (appointment_id) REFERENCES appointments (id)
                )
            """)

            # Medicines table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medicines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    category TEXT,
                    default_dose TEXT,
                    instructions TEXT
                )
            """)

            # Prescriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prescriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    visit_id INTEGER,
                    date TEXT NOT NULL,
                    FOREIGN KEY (patient_id) REFERENCES patients (id),
                    FOREIGN KEY (visit_id) REFERENCES visits (id)
                )
            """)

            # Prescription items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prescription_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prescription_id INTEGER NOT NULL,
                    medicine_id INTEGER NOT NULL,
                    dose TEXT,
                    instructions TEXT,
                    FOREIGN KEY (prescription_id) REFERENCES prescriptions (id),
                    FOREIGN KEY (medicine_id) REFERENCES medicines (id)
                )
            """)


# Global database instance
db = Database()