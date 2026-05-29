"""
API Tests for v1 endpoints - multi-tenant SaaS functionality
"""
import pytest
from app.models import Patient, Medicine, Tenant, User
from app import db


class TestHealthEndpoint:
    """Tests for the health check endpoint"""
    
    def test_health_check(self, client):
        """Test API health endpoint returns 200"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'timestamp' in data


class TestAuthEndpoints:
    """Tests for authentication endpoints"""
    
    def test_login_success(self, client, super_admin_user):
        """Test successful login returns JWT tokens"""
        response = client.post('/api/v1/auth/login', json={
            'username': 'superadmin',
            'password': 'password123'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'superadmin'
    
    def test_login_invalid_credentials(self, client, super_admin_user):
        """Test login with wrong password"""
        response = client.post('/api/v1/auth/login', json={
            'username': 'superadmin',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post('/api/v1/auth/login', json={
            'username': 'admin'
        })
        assert response.status_code == 400
    
    def test_me_endpoint(self, client, auth_headers):
        """Test /auth/me endpoint returns user info"""
        response = client.get('/api/v1/auth/me', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert 'tenant' in data
    
    def test_me_endpoint_unauthorized(self, client):
        """Test /auth/me requires authentication"""
        response = client.get('/api/v1/auth/me')
        assert response.status_code == 401


class TestPatientEndpoints:
    """Tests for patient CRUD endpoints"""
    
    def test_list_patients_empty(self, client, auth_headers):
        """Test listing patients when none exist"""
        response = client.get('/api/v1/patients', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert 'total' in data
        assert len(data['items']) == 0
    
    def test_create_patient(self, client, auth_headers, tenant):
        """Test creating a new patient"""
        response = client.post('/api/v1/patients', headers=auth_headers, json={
            'name': 'John Doe',
            'age': 30,
            'phone': '1234567890',
            'gender': 'Male'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'John Doe'
        assert data['age'] == 30
        assert data['tenant_id'] == tenant.id
    
    def test_get_patient(self, client, auth_headers, app, tenant):
        """Test getting a specific patient"""
        with app.app_context():
            patient = Patient(name='Test Patient', tenant_id=tenant.id)
            db.session.add(patient)
            db.session.commit()
            patient_id = patient.id
        
        response = client.get(f'/api/v1/patients/{patient_id}', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Test Patient'
    
    def test_update_patient(self, client, auth_headers, app, tenant):
        """Test updating a patient"""
        with app.app_context():
            patient = Patient(name='Old Name', tenant_id=tenant.id)
            db.session.add(patient)
            db.session.commit()
            patient_id = patient.id
        
        response = client.put(f'/api/v1/patients/{patient_id}', headers=auth_headers, json={
            'name': 'New Name'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'New Name'
    
    def test_delete_patient(self, client, auth_headers, app, tenant):
        """Test deleting a patient"""
        with app.app_context():
            patient = Patient(name='To Delete', tenant_id=tenant.id)
            db.session.add(patient)
            db.session.commit()
            patient_id = patient.id
        
        response = client.delete(f'/api/v1/patients/{patient_id}', headers=auth_headers)
        assert response.status_code == 200
        
        # Verify deleted
        response = client.get(f'/api/v1/patients/{patient_id}', headers=auth_headers)
        assert response.status_code == 404
    
    def test_search_patients(self, client, auth_headers, app, tenant):
        """Test searching patients"""
        with app.app_context():
            db.session.add(Patient(name='John Smith', tenant_id=tenant.id))
            db.session.add(Patient(name='Jane Doe', tenant_id=tenant.id))
            db.session.commit()
        
        response = client.get('/api/v1/patients?search=John', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) == 1
        assert data['items'][0]['name'] == 'John Smith'


class TestAppointmentEndpoints:
    """Tests for appointment CRUD endpoints"""
    
    def test_create_appointment(self, client, auth_headers, app, tenant):
        """Test creating an appointment"""
        from datetime import date
        with app.app_context():
            patient = Patient(name='Test Patient', tenant_id=tenant.id)
            db.session.add(patient)
            db.session.commit()
            patient_id = patient.id
        
        response = client.post('/api/v1/appointments', headers=auth_headers, json={
            'patient_id': patient_id,
            'date': date.today().isoformat(),
            'time': '10:00',
            'status': 'waiting'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['patient_id'] == patient_id
        assert data['status'] == 'waiting'
    
    def test_list_appointments(self, client, auth_headers):
        """Test listing appointments"""
        response = client.get('/api/v1/appointments', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert 'total' in data
    
    def test_update_appointment_status(self, client, auth_headers, app, tenant):
        """Test updating appointment status"""
        with app.app_context():
            patient = Patient(name='Test Patient', tenant_id=tenant.id)
            db.session.add(patient)
            db.session.commit()
            
            from app.models import Appointment
            from datetime import date
            appt = Appointment(tenant_id=tenant.id, patient_id=patient.id, date=date.today(), time='10:00')
            db.session.add(appt)
            db.session.commit()
            appt_id = appt.id
        
        response = client.put(f'/api/v1/appointments/{appt_id}/status/completed', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'completed'


class TestMedicineEndpoints:
    """Tests for medicine CRUD endpoints"""
    
    def test_create_medicine(self, client, auth_headers):
        """Test creating a medicine"""
        response = client.post('/api/v1/medicines', headers=auth_headers, json={
            'name': 'Aspirin',
            'category': 'Pain Relief',
            'default_dose': '500mg',
            'instructions': 'Take with food'
        })
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Aspirin'
        assert data['category'] == 'Pain Relief'
    
    def test_list_medicines(self, client, auth_headers):
        """Test listing medicines"""
        response = client.get('/api/v1/medicines', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
    
    def test_update_medicine(self, client, auth_headers, app, tenant):
        """Test updating a medicine"""
        with app.app_context():
            medicine = Medicine(name='Old Med', tenant_id=tenant.id)
            db.session.add(medicine)
            db.session.commit()
            med_id = medicine.id
        
        response = client.put(f'/api/v1/medicines/{med_id}', headers=auth_headers, json={
            'name': 'New Med'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'New Med'


class TestDashboardStats:
    """Tests for dashboard statistics endpoint"""
    
    def test_dashboard_stats(self, client, auth_headers, app, tenant):
        """Test dashboard stats endpoint"""
        # Add some data
        with app.app_context():
            db.session.add(Patient(name='Patient 1', tenant_id=tenant.id))
            db.session.add(Patient(name='Patient 2', tenant_id=tenant.id))
            db.session.add(Medicine(name='Medicine 1', tenant_id=tenant.id))
            db.session.commit()
        
        response = client.get('/api/v1/dashboard/stats', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'total_patients' in data
        assert 'today_appointments' in data
        assert 'today_visits' in data
        assert 'total_medicines' in data
        assert data['total_patients'] == 2
        assert data['total_medicines'] == 1


class TestTenantIsolation:
    """Tests to verify API respects tenant isolation"""
    
    def test_cannot_access_other_tenant_data(self, client, app, auth_headers):
        """Test that users cannot access data from other tenants"""
        # Create two tenants with data
        with app.app_context():
            tenant1 = Tenant.query.first()
            tenant2 = Tenant(name='Other Clinic', slug='other-clinic', subscription_plan='free')
            db.session.add(tenant2)
            db.session.commit()
            
            # Add patient to tenant2
            patient2 = Patient(name='Other Patient', tenant_id=tenant2.id)
            db.session.add(patient2)
            db.session.commit()
            other_patient_id = patient2.id
        
        # Try to access with tenant1 user (from auth_headers fixture)
        response = client.get(f'/api/v1/patients/{other_patient_id}', headers=auth_headers)
        # Should return 404 as user can't access other tenant's data
        assert response.status_code == 404