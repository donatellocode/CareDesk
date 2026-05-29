import pytest
from app.models import Patient, Appointment, Visit, Medicine, Prescription, PrescriptionItem, Tenant
from datetime import date
from app import db


class TestTenant:
    """Tests for the Tenant model (multi-tenant SaaS)"""
    
    def test_create_tenant(self, app):
        with app.app_context():
            tenant = Tenant(name='New Clinic', slug='new-clinic', subscription_plan='basic')
            db.session.add(tenant)
            db.session.commit()
            
            assert tenant.id is not None
            assert tenant.name == 'New Clinic'
            assert tenant.slug == 'new-clinic'
            assert tenant.subscription_plan == 'basic'
            assert tenant.is_active is True
    
    def test_tenant_to_dict(self, app):
        with app.app_context():
            tenant = Tenant(name='Test Clinic', slug='test-clinic-2', subscription_plan='premium')
            db.session.add(tenant)
            db.session.commit()
            
            data = tenant.to_dict()
            assert data['name'] == 'Test Clinic'
            assert data['slug'] == 'test-clinic-2'
            assert data['subscription_plan'] == 'premium'
            assert 'id' in data


class TestPatient:
    def test_create_patient(self, app, tenant):
        with app.app_context():
            patient = Patient(
                name='John Doe', 
                age=30, 
                phone='1234567890', 
                gender='Male',
                tenant_id=tenant.id
            )
            db.session.add(patient)
            db.session.commit()
            
            assert patient.id is not None
            assert patient.name == 'John Doe'
            assert patient.age == 30
            assert patient.tenant_id == tenant.id
    
    def test_patient_to_dict(self, app, tenant):
        with app.app_context():
            patient = Patient(
                name='Jane Doe', 
                age=25,
                tenant_id=tenant.id
            )
            db.session.add(patient)
            db.session.commit()
            
            data = patient.to_dict()
            assert data['name'] == 'Jane Doe'
            assert data['age'] == 25
            assert data['tenant_id'] == tenant.id
            assert 'id' in data


class TestAppointment:
    def test_create_appointment(self, app, tenant):
        with app.app_context():
            patient = Patient(name='Test Patient', tenant_id=tenant.id)
            db.session.add(patient)
            db.session.commit()
            
            appt = Appointment(
                tenant_id=tenant.id,
                patient_id=patient.id,
                date=date.today(),
                time='10:00'
            )
            db.session.add(appt)
            db.session.commit()
            
            assert appt.id is not None
            assert appt.status == 'waiting'
            assert appt.tenant_id == tenant.id


class TestMedicine:
    def test_create_medicine(self, app, tenant):
        with app.app_context():
            med = Medicine(
                name='Aspirin',
                category='Pain Relief',
                default_dose='500mg',
                tenant_id=tenant.id
            )
            db.session.add(med)
            db.session.commit()
            
            assert med.id is not None
            assert med.name == 'Aspirin'
            assert med.tenant_id == tenant.id


class TestTenantIsolation:
    """Tests to verify tenant data isolation"""
    
    def test_tenant_patients_isolated(self, app):
        with app.app_context():
            # Create two tenants
            tenant1 = Tenant(name='Clinic 1', slug='clinic-1', subscription_plan='free')
            tenant2 = Tenant(name='Clinic 2', slug='clinic-2', subscription_plan='free')
            db.session.add_all([tenant1, tenant2])
            db.session.commit()
            
            # Add patients to each tenant
            patient1 = Patient(name='Patient 1', tenant_id=tenant1.id)
            patient2 = Patient(name='Patient 2', tenant_id=tenant2.id)
            db.session.add_all([patient1, patient2])
            db.session.commit()
            
            # Verify isolation
            clinic1_patients = Patient.query.filter_by(tenant_id=tenant1.id).all()
            clinic2_patients = Patient.query.filter_by(tenant_id=tenant2.id).all()
            
            assert len(clinic1_patients) == 1
            assert len(clinic2_patients) == 1
            assert clinic1_patients[0].name == 'Patient 1'
            assert clinic2_patients[0].name == 'Patient 2'
