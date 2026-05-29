import pytest
from app import create_app, db
from app.models import User, Tenant


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        # Create test tenant
        tenant = Tenant(name='Test Clinic', slug='test-clinic', subscription_plan='free')
        db.session.add(tenant)
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def tenant(app):
    with app.app_context():
        return Tenant.query.filter_by(slug='test-clinic').first()


@pytest.fixture
def super_admin_user(app, tenant):
    """Create a super admin user for testing"""
    with app.app_context():
        user = User(
            username='superadmin',
            email='superadmin@test.com',
            full_name='Super Admin',
            role='super_admin',
            tenant_id=tenant.id
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def clinic_admin_user(app, tenant):
    """Create a clinic admin user for testing"""
    with app.app_context():
        user = User(
            username='clinicadmin',
            email='clinicadmin@test.com',
            full_name='Clinic Admin',
            role='clinic_admin',
            tenant_id=tenant.id
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def doctor_user(app, tenant):
    """Create a doctor user for testing"""
    with app.app_context():
        user = User(
            username='doctor',
            email='doctor@test.com',
            full_name='Dr. Doctor',
            role='doctor',
            tenant_id=tenant.id
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_headers(app, client, super_admin_user):
    """Get JWT auth headers for API requests"""
    response = client.post('/api/v1/auth/login', json={
        'username': 'superadmin',
        'password': 'password123'
    })
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}
