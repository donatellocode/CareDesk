import pytest
from app.models import Patient, Appointment, Visit, Medicine, Prescription, PrescriptionItem
from datetime import date


class TestPatient:
    def test_create_patient(self, app):
        with app.app_context():
            patient = Patient(name='John Doe', age=30, phone='1234567890', gender='Male')
            db.session.add(patient)
            db.session.commit()
            
            assert patient.id is not None
            assert patient.name == 'John Doe'
            assert patient.age == 30
    
    def test_patient_to_dict(self, app):
        with app.app_context():
            patient = Patient(name='Jane Doe', age=25)
            db.session.add(patient)
            db.session.commit()
            
            data = patient.to_dict()
            assert data['name'] == 'Jane Doe'
            assert data['age'] == 25
            assert 'id' in data


class TestAppointment:
    def test_create_appointment(self, app):
        with app.app_context():
            patient = Patient(name='Test Patient')
            db.session.add(patient)
            db.session.commit()
            
            appt = Appointment(
                patient_id=patient.id,
                date=date.today(),
                time='10:00'
            )
            db.session.add(appt)
            db.session.commit()
            
            assert appt.id is not None
            assert appt.status == 'waiting'


class TestMedicine:
    def test_create_medicine(self, app):
        with app.app_context():
            med = Medicine(
                name='Aspirin',
                category='Pain Relief',
                default_dose='500mg'
            )
            db.session.add(med)
            db.session.commit()
            
            assert med.id is not None
            assert med.name == 'Aspirin'


# Import db here for tests
from app import db
