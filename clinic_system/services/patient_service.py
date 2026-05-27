"""Patient service for business logic."""
from typing import List, Optional
from models import Patient, Visit, Appointment


class PatientService:
    """Service layer for patient operations."""

    @staticmethod
    def get_all_patients() -> List[Patient]:
        """Get all patients."""
        return Patient.get_all()

    @staticmethod
    def search_patients(query: str) -> List[Patient]:
        """Search patients by name or phone."""
        if not query or len(query) < 2:
            return Patient.get_all()
        return Patient.search(query)

    @staticmethod
    def get_patient_by_id(patient_id: int) -> Optional[Patient]:
        """Get patient by ID."""
        return Patient.get_by_id(patient_id)

    @staticmethod
    def create_patient(name: str, age: Optional[int] = None,
                      phone: str = "", gender: str = "",
                      notes: str = "") -> Patient:
        """Create a new patient."""
        return Patient.create(name, age, phone, gender, notes)

    @staticmethod
    def update_patient(patient_id: int, name: str, 
                      age: Optional[int] = None, phone: str = "",
                      gender: str = "", notes: str = "") -> Optional[Patient]:
        """Update an existing patient."""
        patient = Patient.get_by_id(patient_id)
        if patient:
            patient.name = name
            patient.age = age
            patient.phone = phone
            patient.gender = gender
            patient.notes = notes
            patient.update()
            return patient
        return None

    @staticmethod
    def delete_patient(patient_id: int) -> bool:
        """Delete a patient."""
        patient = Patient.get_by_id(patient_id)
        if patient:
            patient.delete()
            return True
        return False

    @staticmethod
    def get_patient_history(patient_id: int) -> dict:
        """Get complete patient history."""
        patient = Patient.get_by_id(patient_id)
        if not patient:
            return {}
        
        appointments = Appointment.get_by_patient(patient_id)
        visits = Visit.get_by_patient(patient_id)
        
        return {
            'patient': patient,
            'appointments': appointments,
            'visits': visits
        }