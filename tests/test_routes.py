import pytest


class TestHomeRoutes:
    def test_index(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'CareDesk' in response.data


class TestPatientRoutes:
    def test_patients_list(self, client):
        response = client.get('/patients/')
        assert response.status_code == 200
    
    def test_new_patient_form(self, client):
        response = client.get('/patients/new')
        assert response.status_code == 200
    
    def test_create_patient(self, client):
        response = client.post('/patients/new', data={
            'name': 'Test Patient',
            'age': '30',
            'gender': 'Male',
            'phone': '1234567890'
        }, follow_redirects=True)
        assert response.status_code == 200


class TestAppointmentRoutes:
    def test_appointments_list(self, client):
        response = client.get('/appointments/')
        assert response.status_code == 200
    
    def test_new_appointment_form(self, client):
        response = client.get('/appointments/new')
        assert response.status_code == 200


class TestVisitRoutes:
    def test_visits_list(self, client):
        response = client.get('/visits/')
        assert response.status_code == 200


class TestMedicineRoutes:
    def test_medicines_list(self, client):
        response = client.get('/medicines/')
        assert response.status_code == 200
    
    def test_new_medicine_form(self, client):
        response = client.get('/medicines/new')
        assert response.status_code == 200


class TestPrescriptionRoutes:
    def test_prescriptions_list(self, client):
        response = client.get('/prescriptions/')
        assert response.status_code == 200
