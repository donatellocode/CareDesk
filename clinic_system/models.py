"""Data models for Clinic Management System."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from database import db


@dataclass
class Patient:
    """Patient model."""
    id: Optional[int] = None
    name: str = ""
    age: Optional[int] = None
    phone: str = ""
    gender: str = ""
    notes: str = ""
    created_at: Optional[str] = None

    @classmethod
    def create(cls, name: str, age: Optional[int] = None, phone: str = "",
               gender: str = "", notes: str = "") -> 'Patient':
        """Create a new patient."""
        query = """INSERT INTO patients (name, age, phone, gender, notes) 
                   VALUES (?, ?, ?, ?, ?)"""
        patient_id = db.execute(query, (name, age, phone, gender, notes))
        return cls.get_by_id(patient_id)

    @classmethod
    def get_by_id(cls, patient_id: int) -> Optional['Patient']:
        """Get patient by ID."""
        row = db.fetch_one("SELECT * FROM patients WHERE id = ?", (patient_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_all(cls) -> List['Patient']:
        """Get all patients."""
        rows = db.fetch_all("SELECT * FROM patients ORDER BY name")
        return [cls.from_row(row) for row in rows]

    @classmethod
    def search(cls, query: str) -> List['Patient']:
        """Search patients by name or phone."""
        rows = db.fetch_all(
            """SELECT * FROM patients 
               WHERE name LIKE ? OR phone LIKE ? 
               ORDER BY name""", 
            (f"%{query}%", f"%{query}%")
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    def from_row(cls, row) -> Optional['Patient']:
        """Create patient from database row."""
        if not row:
            return None
        return cls(
            id=row['id'],
            name=row['name'],
            age=row['age'],
            phone=row['phone'],
            gender=row['gender'],
            notes=row['notes'],
            created_at=row['created_at']
        )

    def update(self) -> None:
        """Update patient in database."""
        query = """UPDATE patients 
                   SET name=?, age=?, phone=?, gender=?, notes=? 
                   WHERE id=?"""
        db.execute(query, (self.name, self.age, self.phone, self.gender, 
                          self.notes, self.id))

    def delete(self) -> None:
        """Delete patient from database."""
        db.execute("DELETE FROM patients WHERE id=?", (self.id,))


@dataclass
class Appointment:
    """Appointment model."""
    id: Optional[int] = None
    patient_id: int = 0
    date: str = ""
    time: str = ""
    status: str = "waiting"

    patient_name: Optional[str] = None

    @classmethod
    def create(cls, patient_id: int, date: str, time: str) -> 'Appointment':
        """Create a new appointment."""
        query = """INSERT INTO appointments (patient_id, date, time) 
                   VALUES (?, ?, ?)"""
        appt_id = db.execute(query, (patient_id, date, time))
        return cls.get_by_id(appt_id)

    @classmethod
    def get_by_id(cls, appt_id: int) -> Optional['Appointment']:
        """Get appointment by ID."""
        row = db.fetch_one(
            """SELECT a.*, p.name as patient_name 
               FROM appointments a 
               JOIN patients p ON a.patient_id = p.id 
               WHERE a.id = ?""", 
            (appt_id,)
        )
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_date(cls, date: str) -> List['Appointment']:
        """Get appointments for a specific date."""
        rows = db.fetch_all(
            """SELECT a.*, p.name as patient_name 
               FROM appointments a 
               JOIN patients p ON a.patient_id = p.id 
               WHERE a.date = ? 
               ORDER BY a.time""", 
            (date,)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    def get_by_patient(cls, patient_id: int) -> List['Appointment']:
        """Get appointments for a patient."""
        rows = db.fetch_all(
            """SELECT a.*, p.name as patient_name 
               FROM appointments a 
               JOIN patients p ON a.patient_id = p.id 
               WHERE a.patient_id = ? 
               ORDER BY a.date DESC, a.time""", 
            (patient_id,)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    def from_row(cls, row) -> Optional['Appointment']:
        """Create appointment from database row."""
        if not row:
            return None
        return cls(
            id=row['id'],
            patient_id=row['patient_id'],
            date=row['date'],
            time=row['time'],
            status=row['status'],
            patient_name=row.get('patient_name')
        )

    def update_status(self, status: str) -> None:
        """Update appointment status."""
        db.execute("UPDATE appointments SET status=? WHERE id=?", 
                   (status, self.id))

    def delete(self) -> None:
        """Delete appointment."""
        db.execute("DELETE FROM appointments WHERE id=?", (self.id,))


@dataclass
class Visit:
    """Visit model."""
    id: Optional[int] = None
    patient_id: int = 0
    appointment_id: Optional[int] = None
    diagnosis: str = ""
    notes: str = ""
    date: str = ""

    patient_name: Optional[str] = None

    @classmethod
    def create(cls, patient_id: int, date: str, 
               diagnosis: str = "", notes: str = "",
               appointment_id: Optional[int] = None) -> 'Visit':
        """Create a new visit."""
        query = """INSERT INTO visits (patient_id, appointment_id, diagnosis, notes, date) 
                   VALUES (?, ?, ?, ?, ?)"""
        visit_id = db.execute(query, 
                             (patient_id, appointment_id, diagnosis, notes, date))
        return cls.get_by_id(visit_id)

    @classmethod
    def get_by_id(cls, visit_id: int) -> Optional['Visit']:
        """Get visit by ID."""
        row = db.fetch_one(
            """SELECT v.*, p.name as patient_name 
               FROM visits v 
               JOIN patients p ON v.patient_id = p.id 
               WHERE v.id = ?""", 
            (visit_id,)
        )
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_patient(cls, patient_id: int) -> List['Visit']:
        """Get visits for a patient."""
        rows = db.fetch_all(
            """SELECT v.*, p.name as patient_name 
               FROM visits v 
               JOIN patients p ON v.patient_id = p.id 
               WHERE v.patient_id = ? 
               ORDER BY v.date DESC""", 
            (patient_id,)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    def from_row(cls, row) -> Optional['Visit']:
        """Create visit from database row."""
        if not row:
            return None
        return cls(
            id=row['id'],
            patient_id=row['patient_id'],
            appointment_id=row['appointment_id'],
            diagnosis=row['diagnosis'],
            notes=row['notes'],
            date=row['date'],
            patient_name=row.get('patient_name')
        )

    def update(self) -> None:
        """Update visit in database."""
        query = """UPDATE visits 
                   SET diagnosis=?, notes=? 
                   WHERE id=?"""
        db.execute(query, (self.diagnosis, self.notes, self.id))

    def delete(self) -> None:
        """Delete visit."""
        db.execute("DELETE FROM visits WHERE id=?", (self.id,))


@dataclass
class Medicine:
    """Medicine model."""
    id: Optional[int] = None
    name: str = ""
    category: str = ""
    default_dose: str = ""
    instructions: str = ""

    @classmethod
    def create(cls, name: str, category: str = "", 
               default_dose: str = "", instructions: str = "") -> 'Medicine':
        """Create a new medicine."""
        query = """INSERT INTO medicines (name, category, default_dose, instructions) 
                   VALUES (?, ?, ?, ?)"""
        med_id = db.execute(query, (name, category, default_dose, instructions))
        return cls.get_by_id(med_id)

    @classmethod
    def get_by_id(cls, med_id: int) -> Optional['Medicine']:
        """Get medicine by ID."""
        row = db.fetch_one("SELECT * FROM medicines WHERE id = ?", (med_id,))
        return cls.from_row(row) if row else None

    @classmethod
    def get_all(cls) -> List['Medicine']:
        """Get all medicines."""
        rows = db.fetch_all("SELECT * FROM medicines ORDER BY name")
        return [cls.from_row(row) for row in rows]

    @classmethod
    def search(cls, query: str) -> List['Medicine']:
        """Search medicines by name or category."""
        rows = db.fetch_all(
            """SELECT * FROM medicines 
               WHERE name LIKE ? OR category LIKE ? 
               ORDER BY name""", 
            (f"%{query}%", f"%{query}%")
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    def from_row(cls, row) -> Optional['Medicine']:
        """Create medicine from database row."""
        if not row:
            return None
        return cls(
            id=row['id'],
            name=row['name'],
            category=row['category'],
            default_dose=row['default_dose'],
            instructions=row['instructions']
        )

    def update(self) -> None:
        """Update medicine in database."""
        query = """UPDATE medicines 
                   SET name=?, category=?, default_dose=?, instructions=? 
                   WHERE id=?"""
        db.execute(query, (self.name, self.category, self.default_dose,
                          self.instructions, self.id))

    def delete(self) -> None:
        """Delete medicine."""
        db.execute("DELETE FROM medicines WHERE id=?", (self.id,))


@dataclass
class Prescription:
    """Prescription model."""
    id: Optional[int] = None
    patient_id: int = 0
    visit_id: Optional[int] = None
    date: str = ""

    patient_name: Optional[str] = None
    items: List['PrescriptionItem'] = None

    @classmethod
    def create(cls, patient_id: int, date: str, 
               visit_id: Optional[int] = None) -> 'Prescription':
        """Create a new prescription."""
        query = """INSERT INTO prescriptions (patient_id, visit_id, date) 
                   VALUES (?, ?, ?)"""
        pres_id = db.execute(query, (patient_id, visit_id, date))
        return cls.get_by_id(pres_id)

    @classmethod
    def get_by_id(cls, pres_id: int) -> Optional['Prescription']:
        """Get prescription by ID with items."""
        row = db.fetch_one(
            """SELECT p.*, pt.name as patient_name 
               FROM prescriptions p 
               JOIN patients pt ON p.patient_id = pt.id 
               WHERE p.id = ?""", 
            (pres_id,)
        )
        if not row:
            return None
        
        prescription = cls.from_row(row)
        prescription.items = PrescriptionItem.get_by_prescription(pres_id)
        return prescription

    @classmethod
    def get_by_patient(cls, patient_id: int) -> List['Prescription']:
        """Get prescriptions for a patient."""
        rows = db.fetch_all(
            """SELECT p.*, pt.name as patient_name 
               FROM prescriptions p 
               JOIN patients pt ON p.patient_id = pt.id 
               WHERE p.patient_id = ? 
               ORDER BY p.date DESC""", 
            (patient_id,)
        )
        prescriptions = []
        for row in rows:
            prescription = cls.from_row(row)
            prescription.items = PrescriptionItem.get_by_prescription(row['id'])
            prescriptions.append(prescription)
        return prescriptions

    @classmethod
    def from_row(cls, row) -> Optional['Prescription']:
        """Create prescription from database row."""
        if not row:
            return None
        return cls(
            id=row['id'],
            patient_id=row['patient_id'],
            visit_id=row['visit_id'],
            date=row['date'],
            patient_name=row.get('patient_name'),
            items=[]
        )

    def add_item(self, medicine_id: int, dose: str, instructions: str) -> None:
        """Add an item to prescription."""
        PrescriptionItem.create(self.id, medicine_id, dose, instructions)
        self.items = PrescriptionItem.get_by_prescription(self.id)

    def delete(self) -> None:
        """Delete prescription and its items."""
        db.execute("DELETE FROM prescription_items WHERE prescription_id=?", 
                   (self.id,))
        db.execute("DELETE FROM prescriptions WHERE id=?", (self.id,))


@dataclass
class PrescriptionItem:
    """Prescription item model."""
    id: Optional[int] = None
    prescription_id: int = 0
    medicine_id: int = 0
    dose: str = ""
    instructions: str = ""

    medicine_name: Optional[str] = None

    @classmethod
    def create(cls, prescription_id: int, medicine_id: int, 
               dose: str, instructions: str) -> 'PrescriptionItem':
        """Create a new prescription item."""
        query = """INSERT INTO prescription_items 
                   (prescription_id, medicine_id, dose, instructions) 
                   VALUES (?, ?, ?, ?)"""
        item_id = db.execute(query, (prescription_id, medicine_id, dose, instructions))
        return cls.get_by_id(item_id)

    @classmethod
    def get_by_id(cls, item_id: int) -> Optional['PrescriptionItem']:
        """Get prescription item by ID."""
        row = db.fetch_one(
            """SELECT pi.*, m.name as medicine_name 
               FROM prescription_items pi 
               JOIN medicines m ON pi.medicine_id = m.id 
               WHERE pi.id = ?""", 
            (item_id,)
        )
        return cls.from_row(row) if row else None

    @classmethod
    def get_by_prescription(cls, prescription_id: int) -> List['PrescriptionItem']:
        """Get all items for a prescription."""
        rows = db.fetch_all(
            """SELECT pi.*, m.name as medicine_name 
               FROM prescription_items pi 
               JOIN medicines m ON pi.medicine_id = m.id 
               WHERE pi.prescription_id = ?""", 
            (prescription_id,)
        )
        return [cls.from_row(row) for row in rows]

    @classmethod
    def from_row(cls, row) -> Optional['PrescriptionItem']:
        """Create prescription item from database row."""
        if not row:
            return None
        return cls(
            id=row['id'],
            prescription_id=row['prescription_id'],
            medicine_id=row['medicine_id'],
            dose=row['dose'],
            instructions=row['instructions'],
            medicine_name=row.get('medicine_name')
        )