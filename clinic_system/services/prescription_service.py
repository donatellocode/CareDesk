"""Prescription service for business logic."""
from typing import List, Optional
from models import Prescription, PrescriptionItem, Medicine, Patient, Visit


class PrescriptionService:
    """Service layer for prescription operations."""

    @staticmethod
    def create_prescription(patient_id: int, visit_id: Optional[int] = None,
                          date: str = "") -> Optional[Prescription]:
        """Create a new prescription."""
        try:
            if not date:
                from datetime import date as date_class
                date = date_class.today().isoformat()
            return Prescription.create(patient_id, date, visit_id)
        except Exception:
            return None

    @staticmethod
    def get_prescription_by_id(prescription_id: int) -> Optional[Prescription]:
        """Get prescription by ID."""
        return Prescription.get_by_id(prescription_id)

    @staticmethod
    def get_prescriptions_by_patient(patient_id: int) -> List[Prescription]:
        """Get all prescriptions for a patient."""
        return Prescription.get_by_patient(patient_id)

    @staticmethod
    def add_medicine_to_prescription(prescription_id: int, medicine_id: int,
                                    dose: str = "", instructions: str = "") -> Optional[PrescriptionItem]:
        """Add a medicine to a prescription."""
        medicine = Medicine.get_by_id(medicine_id)
        if not medicine:
            return None
        
        # Auto-fill from medicine database if not provided
        if not dose:
            dose = medicine.default_dose
        if not instructions:
            instructions = medicine.instructions
        
        try:
            return PrescriptionItem.create(prescription_id, medicine_id, dose, instructions)
        except Exception:
            return None

    @staticmethod
    def update_prescription_item(item_id: int, dose: str,
                                 instructions: str) -> Optional[PrescriptionItem]:
        """Update a prescription item."""
        # This would require adding an update method to PrescriptionItem
        # For now, we return None
        return None

    @staticmethod
    def remove_medicine_from_prescription(prescription_id: int, 
                                         medicine_id: int) -> bool:
        """Remove a medicine from a prescription."""
        from database import db
        try:
            db.execute(
                """DELETE FROM prescription_items 
                   WHERE prescription_id=? AND medicine_id=?""",
                (prescription_id, medicine_id)
            )
            return True
        except Exception:
            return False

    @staticmethod
    def delete_prescription(prescription_id: int) -> bool:
        """Delete a prescription."""
        prescription = Prescription.get_by_id(prescription_id)
        if prescription:
            prescription.delete()
            return True
        return False

    @staticmethod
    def get_prescription_summary(prescription_id: int) -> dict:
        """Get prescription with all details."""
        prescription = Prescription.get_by_id(prescription_id)
        if not prescription:
            return {}
        
        patient = Patient.get_by_id(prescription.patient_id)
        visit = Visit.get_by_id(prescription.visit_id) if prescription.visit_id else None
        
        return {
            'prescription': prescription,
            'patient': patient,
            'visit': visit,
            'items': prescription.items
        }