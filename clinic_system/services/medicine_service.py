"""Medicine service for business logic."""
from typing import List, Optional
from models import Medicine


class MedicineService:
    """Service layer for medicine operations."""

    @staticmethod
    def get_all_medicines() -> List[Medicine]:
        """Get all medicines."""
        return Medicine.get_all()

    @staticmethod
    def search_medicines(query: str) -> List[Medicine]:
        """Search medicines by name or category."""
        if not query or len(query) < 2:
            return Medicine.get_all()
        return Medicine.search(query)

    @staticmethod
    def get_medicine_by_id(medicine_id: int) -> Optional[Medicine]:
        """Get medicine by ID."""
        return Medicine.get_by_id(medicine_id)

    @staticmethod
    def create_medicine(name: str, category: str = "",
                       default_dose: str = "", 
                       instructions: str = "") -> Optional[Medicine]:
        """Create a new medicine."""
        try:
            return Medicine.create(name, category, default_dose, instructions)
        except Exception:
            return None

    @staticmethod
    def update_medicine(medicine_id: int, name: str,
                       category: str = "", default_dose: str = "",
                       instructions: str = "") -> Optional[Medicine]:
        """Update an existing medicine."""
        medicine = Medicine.get_by_id(medicine_id)
        if medicine:
            medicine.name = name
            medicine.category = category
            medicine.default_dose = default_dose
            medicine.instructions = instructions
            try:
                medicine.update()
                return medicine
            except Exception:
                return None
        return None

    @staticmethod
    def delete_medicine(medicine_id: int) -> bool:
        """Delete a medicine."""
        medicine = Medicine.get_by_id(medicine_id)
        if medicine:
            medicine.delete()
            return True
        return False

    @staticmethod
    def get_medicine_categories() -> List[str]:
        """Get list of unique medicine categories."""
        medicines = Medicine.get_all()
        categories = set()
        for med in medicines:
            if med.category:
                categories.add(med.category)
        return sorted(list(categories))