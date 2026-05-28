# CareDesk - Clinic Management System

A modern, production-ready Flask web application for managing clinic operations including patients, appointments, visits, medicines, and prescriptions.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Dashboard** - Real-time overview with clinic statistics
- **Patient Management** - Complete CRUD operations with search
- **Appointment Scheduling** - Date/time based scheduling with status tracking
- **Visit Records** - Track patient visits with diagnosis
- **Medicine Inventory** - Manage medications with dosage information
- **Prescriptions** - Create and manage patient prescriptions
- **RESTful API** - JSON endpoints for all resources
- **Pagination** - Efficient data browsing with paginated lists
- **Search** - Quick search across patients and medicines

## Tech Stack

- **Backend**: Flask 3.0, SQLAlchemy, Flask-Migrate
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, Jinja2 templates
- **Forms**: Flask-WTF with validation
- **Deployment**: Docker, Gunicorn

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/donatellocode/CareDesk.git
cd CareDesk

# Start with Docker Compose
docker-compose up -d

# The app will be available at http://localhost:8000
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/donatellocode/CareDesk.git
cd CareDesk

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py

# The app will be available at http://localhost:5000
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Application environment | `development` |
| `SECRET_KEY` | Secret key for sessions | Required in production |
| `DATABASE_URL` | Database connection string | SQLite local file |

### Configuration Files

- `.env.example` - Example environment variables
- `config.py` - Application configuration classes

## Database Migrations

```bash
# Initialize migrations (first time)
flask db init

# Create a migration
flask db migrate -m "Your message"

# Apply migrations
flask db upgrade
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Using Docker

```bash
# Production with PostgreSQL
docker-compose -f docker-compose.yml up -d
```

### Environment Setup for Production

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-random-key
export DATABASE_URL=postgresql://user:pass@host:5432/caredesk
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_routes.py
```

## API Endpoints

### Patients
- `GET /patients/` - List patients
- `POST /patients/new` - Create patient
- `GET /patients/<id>` - View patient
- `PUT /patients/<id>/edit` - Update patient
- `DELETE /patients/<id>/delete` - Delete patient
- `GET /patients/api/list` - API: List all patients (JSON)
- `GET /patients/api/<id>` - API: Get patient (JSON)

### Appointments
- `GET /appointments/` - List appointments
- `POST /appointments/new` - Create appointment
- `PUT /appointments/<id>/edit` - Update appointment
- `DELETE /appointments/<id>/delete` - Delete appointment
- `GET /appointments/<id>/status/<status>` - Update status

### Visits
- `GET /visits/` - List visits
- `POST /visits/new` - Create visit
- `GET /visits/<id>` - View visit
- `PUT /visits/<id>/edit` - Update visit
- `DELETE /visits/<id>/delete` - Delete visit

### Medicines
- `GET /medicines/` - List medicines
- `POST /medicines/new` - Add medicine
- `PUT /medicines/<id>/edit` - Update medicine
- `DELETE /medicines/<id>/delete` - Delete medicine

### Prescriptions
- `GET /prescriptions/` - List prescriptions
- `POST /prescriptions/new` - Create prescription
- `GET /prescriptions/<id>` - View prescription
- `DELETE /prescriptions/<id>/delete` - Delete prescription

## Project Structure

```
CareDesk/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms definitions
│   ├── routes/              # Route blueprints
│   │   ├── home.py
│   │   ├── patients.py
│   │   ├── appointments.py
│   │   ├── visits.py
│   │   ├── medicines.py
│   │   └── prescriptions.py
│   ├── templates/           # Jinja2 templates
│   └── static/
│       └── css/
├── tests/                   # Test suite
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── run.py                   # Entry point
├── Dockerfile
└── docker-compose.yml
```

## Security Features

- CSRF protection via Flask-WTF
- SQL injection prevention via SQLAlchemy ORM
- Secure session cookies (HttpOnly, Secure, SameSite)
- Input validation on all forms
- Error handlers for 404, 500, etc.
- Production-ready configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
