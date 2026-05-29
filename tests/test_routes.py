import pytest
from app.models import User, Tenant
from app import db


@pytest.fixture
def authenticated_client(client, app):
    """Create an authenticated test client with a logged-in user"""
    with app.app_context():
        # Get default tenant
        tenant = Tenant.query.first()
        if not tenant:
            tenant = Tenant(name='Default', slug='default', subscription_plan='free')
            db.session.add(tenant)
            db.session.commit()
        
        # Create test user
        user = User.query.filter_by(username='testuser').first()
        if not user:
            user = User(
                username='testuser',
                email='test@test.com',
                full_name='Test User',
                role='clinic_admin',
                tenant_id=tenant.id
            )
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        # Login
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
    
    return client


class TestHomeRoutes:
    def test_index(self, authenticated_client):
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'CareDesk' in response.data


class TestPatientRoutes:
    def test_patients_list(self, authenticated_client):
        response = authenticated_client.get('/patients/')
        assert response.status_code == 200
    
    def test_new_patient_form(self, authenticated_client):
        response = authenticated_client.get('/patients/new')
        assert response.status_code == 200
    
    def test_create_patient(self, authenticated_client):
        response = authenticated_client.post('/patients/new', data={
            'name': 'Test Patient',
            'age': '30',
            'gender': 'Male',
            'phone': '1234567890'
        }, follow_redirects=True)
        assert response.status_code == 200


class TestAppointmentRoutes:
    def test_appointments_list(self, authenticated_client):
        response = authenticated_client.get('/appointments/')
        assert response.status_code == 200
    
    def test_new_appointment_form(self, authenticated_client):
        response = authenticated_client.get('/appointments/new')
        assert response.status_code == 200


class TestVisitRoutes:
    def test_visits_list(self, authenticated_client):
        response = authenticated_client.get('/visits/')
        assert response.status_code == 200


class TestMedicineRoutes:
    def test_medicines_list(self, authenticated_client):
        response = authenticated_client.get('/medicines/')
        assert response.status_code == 200
    
    def test_new_medicine_form(self, authenticated_client):
        response = authenticated_client.get('/medicines/new')
        assert response.status_code == 200


class TestPrescriptionRoutes:
    def test_prescriptions_list(self, authenticated_client):
        response = authenticated_client.get('/prescriptions/')
        assert response.status_code == 200
