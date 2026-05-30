# CareDesk v2 — Enterprise SaaS Clinic Platform

## System Overview

CareDesk is a production-ready, multi-tenant SaaS clinic management platform built with Flask. It provides comprehensive management of patients, appointments, visits, medicines, and prescriptions with a modern REST API architecture.

### Features
- Multi-tenant architecture with complete data isolation
- JWT authentication for REST API
- Session authentication for web interface
- Role-based access control (6 roles)
- Versioned REST API v1
- Full CRUD operations for all entities
- Dashboard analytics
- Comprehensive test suite (37 tests)

---

## Architecture

### Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Flask 3.0, SQLAlchemy ORM, Flask-Migrate |
| **Authentication** | Flask-JWT-Extended (JWT), Flask-Login (sessions) |
| **Database** | SQLite (development), PostgreSQL (production) |
| **Frontend** | HTML5, CSS3, Jinja2 templates |
| **Forms** | Flask-WTF with validation |
| **API** | RESTful JSON API v1 |
| **Deployment** | Docker, Gunicorn |

### Project Structure

```
CareDesk/
├── app/
│   ├── __init__.py          # Application factory, JWT init, tenant setup
│   ├── models.py             # All database models with mixins
│   ├── forms.py              # WTForms definitions
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py            # REST API v1
│   │   ├── home.py           # Dashboard
│   │   ├── auth.py           # Authentication & user management
│   │   ├── patients.py       # Patient CRUD
│   │   ├── appointments.py   # Appointment management
│   │   ├── visits.py         # Visit records
│   │   ├── medicines.py       # Medicine inventory
│   │   └── prescriptions.py   # Prescription management
│   ├── templates/            # Jinja2 templates
│   └── static/               # CSS, JS, images
├── tests/
│   ├── conftest.py           # Test fixtures (multi-tenant)
│   ├── test_models.py        # Model tests
│   ├── test_api.py           # API v1 tests
│   └── test_routes.py         # Web route tests
├── config.py                 # Configuration classes
├── requirements.txt          # Dependencies
├── run.py                    # Entry point
├── Dockerfile
├── docker-compose.yml
└── SYSTEM_SUMMARY.md         # This documentation
```

---

## Data Models

### Model Mixins

The application uses mixins for common functionality:

```python
class TimestampMixin:
    """Provides created_at and updated_at fields with timezone-aware datetimes"""
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=..., onupdate=...)


class TenantMixin:
    """Provides tenant_id foreign key for multi-tenant models"""
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id', ondelete='CASCADE'))
```

### Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Tenant    │       │    User     │       │   Patient   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ name        │◄──────│ tenant_id   │       │ tenant_id   │
│ slug        │       │ username    │       │ name        │
│ subscription│       │ email       │       │ age         │
│ settings    │       │ role        │       │ phone       │
│ timestamps  │       │ timestamps  │       │ timestamps  │
└─────────────┘       └─────────────┘       └─────────────┘
                                                 │
                            ┌────────────────────┼────────────────────┐
                            ▼                    ▼                    ▼
                    ┌─────────────┐       ┌─────────────┐      ┌─────────────┐
                    │Appointment │       │    Visit    │      │Prescription│
                    ├─────────────┤       ├─────────────┤      ├─────────────┤
                    │ id (PK)     │       │ id (PK)     │      │ id (PK)     │
                    │ tenant_id   │       │ tenant_id   │      │ tenant_id   │
                    │ patient_id  │◄─────│ patient_id  │──┐   │ patient_id  │
                    │ date        │       │ diagnosis   │  │   │ visit_id    │──┐
                    │ time        │       │ notes       │  │   │ date        │  │
                    │ status      │       │ timestamps  │  │   │ timestamps  │  │
                    │ timestamps  │       └─────────────┘  │   └─────────────┘  │
                    └─────────────┘                         │         │          │
                            │                               │         ▼          │
                            └───────────────────────────────┘   ┌─────────────────┐
                                    ┌─────────────┐            │PrescriptionItem │
                                    │ Medicine   │              ├─────────────────┤
                                    ├─────────────┤              │ id (PK)         │
                                    │ id (PK)     │◄────────────│ prescription_id │
                                    │ tenant_id   │              │ medicine_id     │
                                    │ name        │              │ dose            │
                                    │ category     │              │ instructions    │
                                    │ timestamps  │              └─────────────────┘
                                    └─────────────┘
```

### All Models

| Model | Mixins | Description |
|-------|--------|-------------|
| `Tenant` | TimestampMixin | Clinic/organization |
| `User` | TimestampMixin | Users with roles |
| `Patient` | TimestampMixin, TenantMixin | Patient records |
| `Appointment` | TimestampMixin, TenantMixin | Scheduled appointments |
| `Visit` | TimestampMixin, TenantMixin | Patient visits |
| `Medicine` | TimestampMixin, TenantMixin | Medicine inventory |
| `Prescription` | TimestampMixin, TenantMixin | Prescriptions |
| `PrescriptionItem` | - | Prescription line items |

---

## User Roles & Permissions

| Role | Description | Permissions |
|------|-------------|-------------|
| `super_admin` | Platform administrator | Manage all tenants, users, settings |
| `clinic_admin` | Clinic administrator | Manage clinic users, all clinic data |
| `doctor` | Medical professional | View/edit patients, appointments, visits, prescriptions |
| `nurse` | Nursing staff | View/edit patients, visits, basic operations |
| `receptionist` | Front desk | Manage appointments, patient registration |
| `patient` | Patient portal | View own records (future) |

---

## Authentication

### JWT Authentication (API)

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {...}
}
```

### Session Authentication (Web)

Traditional login form for Jinja2 web interface.

---

## REST API v1

### Base URL

```
/api/v1/
```

### API Decorators

The API uses decorators for authentication and authorization:

```python
@jwt_required()           # Require valid JWT
@tenant_required          # Enforce tenant isolation
@role_required('admin')   # Require specific role
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/auth/login` | Login, returns JWT tokens |
| `POST` | `/auth/refresh` | Refresh access token |
| `GET` | `/auth/me` | Get current user info |
| `GET` | `/patients` | List patients (paginated) |
| `POST` | `/patients` | Create patient |
| `GET` | `/patients/<id>` | Get patient |
| `PUT` | `/patients/<id>` | Update patient |
| `DELETE` | `/patients/<id>` | Delete patient |
| `GET` | `/appointments` | List appointments |
| `POST` | `/appointments` | Create appointment |
| `PUT` | `/appointments/<id>` | Update appointment |
| `PUT` | `/appointments/<id>/status/<status>` | Update status |
| `DELETE` | `/appointments/<id>` | Delete appointment |
| `GET` | `/visits` | List visits |
| `POST` | `/visits` | Create visit |
| `GET` | `/visits/<id>` | Get visit |
| `PUT` | `/visits/<id>` | Update visit |
| `DELETE` | `/visits/<id>` | Delete visit |
| `GET` | `/medicines` | List medicines |
| `POST` | `/medicines` | Create medicine |
| `PUT` | `/medicines/<id>` | Update medicine |
| `DELETE` | `/medicines/<id>` | Delete medicine |
| `GET` | `/prescriptions` | List prescriptions |
| `POST` | `/prescriptions` | Create prescription with items |
| `GET` | `/prescriptions/<id>` | Get prescription |
| `DELETE` | `/prescriptions/<id>` | Delete prescription |
| `GET` | `/dashboard/stats` | Get dashboard statistics |
| `GET` | `/tenants` | List all tenants (super_admin) |
| `POST` | `/tenants` | Create tenant (super_admin) |
| `GET` | `/tenants/<id>` | Get tenant |
| `PUT` | `/tenants/<id>` | Update tenant |
| `GET` | `/users` | List users in tenant |
| `POST` | `/users` | Create user |

### API Example

```bash
# Create Patient
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "age": 30,
    "phone": "123-456-7890",
    "gender": "Male"
  }'
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment | `development` |
| `SECRET_KEY` | Session secret | Required in production |
| `JWT_SECRET_KEY` | JWT signing key | Required in production |
| `DATABASE_URL` | Database connection | SQLite local file |

### Configuration Classes

| Class | Environment | Features |
|-------|-------------|----------|
| `DevelopmentConfig` | development | Debug, no CSRF |
| `ProductionConfig` | production | No debug, required secrets |
| `TestingConfig` | testing | In-memory DB, short JWT expiry |

---

## Deployment

### Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# App at http://localhost:8000
# API at http://localhost:8000/api/v1/
```

### Manual

```bash
pip install -r requirements.txt
python run.py  # Development at http://localhost:5000
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"  # Production
```

---

## Testing

### Run Tests

```bash
pytest              # All tests
pytest --cov=app    # With coverage
```

### Test Results

**37 tests passing** covering:
- Tenant model & isolation
- API authentication
- CRUD operations
- Dashboard statistics
- Role-based access
- Web routes

---

## Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | super_admin |
| clinic_admin | clinic123 | clinic_admin |

---

## Dependencies

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-WTF==1.2.1
Flask-JWT-Extended==4.6.0
Flask-Login==0.6.3
WTForms==3.1.1
email_validator==2.1.0
python-dotenv==1.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
```

---

## Future Roadmap

### Phase 2: Frontend Modernization
- [ ] Next.js 15 frontend
- [ ] TypeScript integration
- [ ] Tailwind CSS + ShadCN UI
- [ ] Dark/Light themes

### Phase 3: SaaS Features
- [ ] Stripe billing integration
- [ ] Subscription plans
- [ ] Usage limits per plan

### Phase 4: Enterprise Features
- [ ] White-label customization
- [ ] Audit logging
- [ ] AI medical notes
- [ ] Multi-branch clinics

---

## License

MIT License