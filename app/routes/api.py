"""
API v1 Blueprint - Versioned REST API for multi-tenant SaaS
All endpoints require JWT authentication and enforce tenant isolation.
"""
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models import Patient, Appointment, Visit, Medicine, Prescription, PrescriptionItem, User, Tenant
from sqlalchemy import or_, func
from datetime import datetime, date
from functools import wraps

bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Helper function to get tenant_id from JWT
def get_tenant_id():
    try:
        jwt = get_jwt()
        return jwt.get('tenant_id', 0)
    except:
        return 0


# Role-based access decorators
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            jwt_data = get_jwt()
            user_role = jwt_data.get('role', '')
            if user_role not in roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Tenant isolation decorator
def tenant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tenant_id = get_tenant_id()
        if tenant_id == 0:
            return jsonify({'error': 'Tenant ID not found in token'}), 401
        g.tenant_id = tenant_id
        return f(*args, **kwargs)
    return decorated_function


# ============= HEALTH CHECK =============

@bp.route('/health')
def health():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0',
        'timestamp': datetime.utcnow().isoformat()
    })


# ============= AUTH ENDPOINTS =============

@bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT tokens"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 401
    
    # Create access token with tenant info in claims
    from flask_jwt_extended import create_access_token, create_refresh_token
    
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            'tenant_id': user.tenant_id,
            'role': user.role,
            'full_name': user.full_name
        }
    )
    refresh_token = create_refresh_token(identity=str(user.id))
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    from flask_jwt_extended import create_access_token
    
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    
    if not user or not user.is_active:
        return jsonify({'error': 'User not found or inactive'}), 401
    
    access_token = create_access_token(
        identity=identity,
        additional_claims={
            'tenant_id': user.tenant_id,
            'role': user.role,
            'full_name': user.full_name
        }
    )
    
    return jsonify({'access_token': access_token}), 200


@bp.route('/auth/me', methods=['GET'])
@jwt_required()
@tenant_required
def me():
    """Get current user info"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict(),
        'tenant': user.tenant.to_dict() if user.tenant else None
    }), 200


# ============= TENANT ENDPOINTS (Super Admin Only) =============

@bp.route('/tenants', methods=['GET'])
@jwt_required()
@role_required('super_admin')
def list_tenants():
    """List all tenants (super admin only)"""
    tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tenants]), 200


@bp.route('/tenants', methods=['POST'])
@jwt_required()
@role_required('super_admin')
def create_tenant():
    """Create a new tenant (super admin only)"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('slug'):
        return jsonify({'error': 'Name and slug are required'}), 400
    
    if Tenant.query.filter_by(slug=data['slug']).first():
        return jsonify({'error': 'Slug already exists'}), 400
    
    tenant = Tenant(
        name=data['name'],
        slug=data['slug'],
        subscription_plan=data.get('subscription_plan', 'free'),
        settings=data.get('settings', {})
    )
    
    db.session.add(tenant)
    db.session.commit()
    
    return jsonify(tenant.to_dict()), 201


@bp.route('/tenants/<int:tenant_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_tenant(tenant_id):
    """Get tenant details (super admin or own tenant)"""
    jwt_data = get_jwt()
    current_tenant_id = jwt_data.get('tenant_id')
    role = jwt_data.get('role')
    
    if role != 'super_admin' and current_tenant_id != tenant_id:
        return jsonify({'error': 'Access denied'}), 403
    
    tenant = Tenant.query.get_or_404(tenant_id)
    return jsonify(tenant.to_dict()), 200


@bp.route('/tenants/<int:tenant_id>', methods=['PUT'])
@jwt_required()
@role_required('super_admin', 'clinic_admin')
def update_tenant(tenant_id):
    """Update tenant (super admin or clinic admin of own tenant)"""
    jwt_data = get_jwt()
    current_tenant_id = jwt_data.get('tenant_id')
    role = jwt_data.get('role')
    
    if role == 'clinic_admin' and current_tenant_id != tenant_id:
        return jsonify({'error': 'Access denied'}), 403
    
    tenant = Tenant.query.get_or_404(tenant_id)
    data = request.get_json()
    
    if 'name' in data:
        tenant.name = data['name']
    if 'subscription_plan' in data and role == 'super_admin':
        tenant.subscription_plan = data['subscription_plan']
    if 'is_active' in data and role == 'super_admin':
        tenant.is_active = data['is_active']
    if 'settings' in data:
        tenant.settings = data['settings']
    
    db.session.commit()
    return jsonify(tenant.to_dict()), 200


# ============= PATIENT ENDPOINTS =============

@bp.route('/patients', methods=['GET'])
@jwt_required()
@tenant_required
def list_patients():
    """List patients with pagination and search"""
    tenant_id = g.tenant_id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    
    query = Patient.query.filter_by(tenant_id=tenant_id)
    
    if search:
        query = query.filter(
            or_(Patient.name.ilike(f'%{search}%'), Patient.phone.ilike(f'%{search}%'))
        )
    
    patients = query.order_by(Patient.name).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [p.to_dict() for p in patients.items],
        'total': patients.total,
        'pages': patients.pages,
        'current_page': page
    }), 200


@bp.route('/patients', methods=['POST'])
@jwt_required()
@tenant_required
def create_patient():
    """Create a new patient"""
    tenant_id = g.tenant_id
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    patient = Patient(
        tenant_id=tenant_id,
        name=data['name'],
        age=data.get('age'),
        phone=data.get('phone'),
        gender=data.get('gender'),
        notes=data.get('notes')
    )
    
    db.session.add(patient)
    db.session.commit()
    
    return jsonify(patient.to_dict()), 201


@bp.route('/patients/<int:patient_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_patient(patient_id):
    """Get patient details"""
    tenant_id = g.tenant_id
    patient = Patient.query.filter_by(id=patient_id, tenant_id=tenant_id).first_or_404()
    return jsonify(patient.to_dict()), 200


@bp.route('/patients/<int:patient_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_patient(patient_id):
    """Update patient"""
    tenant_id = g.tenant_id
    patient = Patient.query.filter_by(id=patient_id, tenant_id=tenant_id).first_or_404()
    data = request.get_json()
    
    if 'name' in data:
        patient.name = data['name']
    if 'age' in data:
        patient.age = data['age']
    if 'phone' in data:
        patient.phone = data['phone']
    if 'gender' in data:
        patient.gender = data['gender']
    if 'notes' in data:
        patient.notes = data['notes']
    
    db.session.commit()
    return jsonify(patient.to_dict()), 200


@bp.route('/patients/<int:patient_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_patient(patient_id):
    """Delete patient"""
    tenant_id = g.tenant_id
    patient = Patient.query.filter_by(id=patient_id, tenant_id=tenant_id).first_or_404()
    
    db.session.delete(patient)
    db.session.commit()
    
    return jsonify({'message': 'Patient deleted'}), 200


# ============= APPOINTMENT ENDPOINTS =============

@bp.route('/appointments', methods=['GET'])
@jwt_required()
@tenant_required
def list_appointments():
    """List appointments with pagination"""
    tenant_id = g.tenant_id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    date_filter = request.args.get('date')
    status = request.args.get('status')
    
    query = Appointment.query.filter_by(tenant_id=tenant_id)
    
    if date_filter:
        query = query.filter_by(date=date_filter)
    if status:
        query = query.filter_by(status=status)
    
    appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [a.to_dict() for a in appointments.items],
        'total': appointments.total,
        'pages': appointments.pages,
        'current_page': page
    }), 200


@bp.route('/appointments', methods=['POST'])
@jwt_required()
@tenant_required
def create_appointment():
    """Create a new appointment"""
    tenant_id = g.tenant_id
    data = request.get_json()
    
    if not data or not data.get('patient_id') or not data.get('date') or not data.get('time'):
        return jsonify({'error': 'patient_id, date, and time are required'}), 400
    
    # Verify patient belongs to tenant
    patient = Patient.query.filter_by(id=data['patient_id'], tenant_id=tenant_id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Parse date - handle both string and date object
    appt_date = data['date']
    if isinstance(appt_date, str):
        from datetime import datetime
        appt_date = datetime.strptime(appt_date, '%Y-%m-%d').date()
    
    appointment = Appointment(
        tenant_id=tenant_id,
        patient_id=data['patient_id'],
        date=appt_date,
        time=data['time'],
        status=data.get('status', 'waiting'),
        notes=data.get('notes')
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify(appointment.to_dict()), 201


@bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_appointment(appointment_id):
    """Update appointment"""
    tenant_id = g.tenant_id
    appointment = Appointment.query.filter_by(id=appointment_id, tenant_id=tenant_id).first_or_404()
    data = request.get_json()
    
    if 'patient_id' in data:
        patient = Patient.query.filter_by(id=data['patient_id'], tenant_id=tenant_id).first()
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        appointment.patient_id = data['patient_id']
    if 'date' in data:
        appt_date = data['date']
        if isinstance(appt_date, str):
            from datetime import datetime
            appt_date = datetime.strptime(appt_date, '%Y-%m-%d').date()
        appointment.date = appt_date
    if 'time' in data:
        appointment.time = data['time']
    if 'status' in data:
        appointment.status = data['status']
    if 'notes' in data:
        appointment.notes = data['notes']
    
    db.session.commit()
    return jsonify(appointment.to_dict()), 200


@bp.route('/appointments/<int:appointment_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_appointment(appointment_id):
    """Delete appointment"""
    tenant_id = g.tenant_id
    appointment = Appointment.query.filter_by(id=appointment_id, tenant_id=tenant_id).first_or_404()
    
    db.session.delete(appointment)
    db.session.commit()
    
    return jsonify({'message': 'Appointment deleted'}), 200


@bp.route('/appointments/<int:appointment_id>/status/<status>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_appointment_status(appointment_id, status):
    """Update appointment status"""
    tenant_id = g.tenant_id
    appointment = Appointment.query.filter_by(id=appointment_id, tenant_id=tenant_id).first_or_404()
    
    if status not in ['waiting', 'completed', 'cancelled']:
        return jsonify({'error': 'Invalid status'}), 400
    
    appointment.status = status
    db.session.commit()
    
    return jsonify(appointment.to_dict()), 200


# ============= VISIT ENDPOINTS =============

@bp.route('/visits', methods=['GET'])
@jwt_required()
@tenant_required
def list_visits():
    """List visits with pagination"""
    tenant_id = g.tenant_id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    visits = Visit.query.filter_by(tenant_id=tenant_id)\
        .order_by(Visit.date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [v.to_dict() for v in visits.items],
        'total': visits.total,
        'pages': visits.pages,
        'current_page': page
    }), 200


@bp.route('/visits', methods=['POST'])
@jwt_required()
@tenant_required
def create_visit():
    """Create a new visit"""
    tenant_id = g.tenant_id
    data = request.get_json()
    
    if not data or not data.get('patient_id') or not data.get('date'):
        return jsonify({'error': 'patient_id and date are required'}), 400
    
    # Verify patient belongs to tenant
    patient = Patient.query.filter_by(id=data['patient_id'], tenant_id=tenant_id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Parse date - handle both string and date object
    visit_date = data['date']
    if isinstance(visit_date, str):
        from datetime import datetime
        visit_date = datetime.strptime(visit_date, '%Y-%m-%d').date()
    
    visit = Visit(
        tenant_id=tenant_id,
        patient_id=data['patient_id'],
        appointment_id=data.get('appointment_id'),
        diagnosis=data.get('diagnosis'),
        notes=data.get('notes'),
        date=visit_date
    )
    
    db.session.add(visit)
    db.session.commit()
    
    return jsonify(visit.to_dict()), 201


@bp.route('/visits/<int:visit_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_visit(visit_id):
    """Get visit details"""
    tenant_id = g.tenant_id
    visit = Visit.query.filter_by(id=visit_id, tenant_id=tenant_id).first_or_404()
    return jsonify(visit.to_dict()), 200


@bp.route('/visits/<int:visit_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_visit(visit_id):
    """Update visit"""
    tenant_id = g.tenant_id
    visit = Visit.query.filter_by(id=visit_id, tenant_id=tenant_id).first_or_404()
    data = request.get_json()
    
    if 'diagnosis' in data:
        visit.diagnosis = data['diagnosis']
    if 'notes' in data:
        visit.notes = data['notes']
    
    db.session.commit()
    return jsonify(visit.to_dict()), 200


@bp.route('/visits/<int:visit_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_visit(visit_id):
    """Delete visit"""
    tenant_id = g.tenant_id
    visit = Visit.query.filter_by(id=visit_id, tenant_id=tenant_id).first_or_404()
    
    db.session.delete(visit)
    db.session.commit()
    
    return jsonify({'message': 'Visit deleted'}), 200


# ============= MEDICINE ENDPOINTS =============

@bp.route('/medicines', methods=['GET'])
@jwt_required()
@tenant_required
def list_medicines():
    """List medicines with pagination and search"""
    tenant_id = g.tenant_id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category')
    
    query = Medicine.query.filter_by(tenant_id=tenant_id)
    
    if search:
        query = query.filter(Medicine.name.ilike(f'%{search}%'))
    if category:
        query = query.filter_by(category=category)
    
    medicines = query.order_by(Medicine.name)\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [m.to_dict() for m in medicines.items],
        'total': medicines.total,
        'pages': medicines.pages,
        'current_page': page
    }), 200


@bp.route('/medicines', methods=['POST'])
@jwt_required()
@tenant_required
def create_medicine():
    """Create a new medicine"""
    tenant_id = g.tenant_id
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400
    
    medicine = Medicine(
        tenant_id=tenant_id,
        name=data['name'],
        category=data.get('category'),
        default_dose=data.get('default_dose'),
        instructions=data.get('instructions')
    )
    
    db.session.add(medicine)
    db.session.commit()
    
    return jsonify(medicine.to_dict()), 201


@bp.route('/medicines/<int:medicine_id>', methods=['PUT'])
@jwt_required()
@tenant_required
def update_medicine(medicine_id):
    """Update medicine"""
    tenant_id = g.tenant_id
    medicine = Medicine.query.filter_by(id=medicine_id, tenant_id=tenant_id).first_or_404()
    data = request.get_json()
    
    if 'name' in data:
        medicine.name = data['name']
    if 'category' in data:
        medicine.category = data['category']
    if 'default_dose' in data:
        medicine.default_dose = data['default_dose']
    if 'instructions' in data:
        medicine.instructions = data['instructions']
    
    db.session.commit()
    return jsonify(medicine.to_dict()), 200


@bp.route('/medicines/<int:medicine_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_medicine(medicine_id):
    """Delete medicine"""
    tenant_id = g.tenant_id
    medicine = Medicine.query.filter_by(id=medicine_id, tenant_id=tenant_id).first_or_404()
    
    db.session.delete(medicine)
    db.session.commit()
    
    return jsonify({'message': 'Medicine deleted'}), 200


# ============= PRESCRIPTION ENDPOINTS =============

@bp.route('/prescriptions', methods=['GET'])
@jwt_required()
@tenant_required
def list_prescriptions():
    """List prescriptions with pagination"""
    tenant_id = g.tenant_id
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    patient_id = request.args.get('patient_id', type=int)
    
    query = Prescription.query.filter_by(tenant_id=tenant_id)
    
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
    
    prescriptions = query.order_by(Prescription.date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'items': [p.to_dict() for p in prescriptions.items],
        'total': prescriptions.total,
        'pages': prescriptions.pages,
        'current_page': page
    }), 200


@bp.route('/prescriptions', methods=['POST'])
@jwt_required()
@tenant_required
def create_prescription():
    """Create a new prescription with items"""
    tenant_id = g.tenant_id
    data = request.get_json()
    
    if not data or not data.get('patient_id') or not data.get('date'):
        return jsonify({'error': 'patient_id and date are required'}), 400
    
    # Verify patient belongs to tenant
    patient = Patient.query.filter_by(id=data['patient_id'], tenant_id=tenant_id).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Parse date - handle both string and date object
    rx_date = data['date']
    if isinstance(rx_date, str):
        from datetime import datetime
        rx_date = datetime.strptime(rx_date, '%Y-%m-%d').date()
    
    prescription = Prescription(
        tenant_id=tenant_id,
        patient_id=data['patient_id'],
        visit_id=data.get('visit_id'),
        notes=data.get('notes'),
        date=rx_date
    )
    
    db.session.add(prescription)
    db.session.flush()  # Get prescription ID
    
    # Add prescription items
    if 'items' in data and isinstance(data['items'], list):
        for item_data in data['items']:
            if item_data.get('medicine_id') and item_data.get('dose'):
                # Verify medicine belongs to tenant
                medicine = Medicine.query.filter_by(id=item_data['medicine_id'], tenant_id=tenant_id).first()
                if medicine:
                    item = PrescriptionItem(
                        prescription_id=prescription.id,
                        medicine_id=item_data['medicine_id'],
                        dose=item_data['dose'],
                        instructions=item_data.get('instructions')
                    )
                    db.session.add(item)
    
    db.session.commit()
    return jsonify(prescription.to_dict()), 201


@bp.route('/prescriptions/<int:prescription_id>', methods=['GET'])
@jwt_required()
@tenant_required
def get_prescription(prescription_id):
    """Get prescription details with items"""
    tenant_id = g.tenant_id
    prescription = Prescription.query.filter_by(id=prescription_id, tenant_id=tenant_id).first_or_404()
    return jsonify(prescription.to_dict()), 200


@bp.route('/prescriptions/<int:prescription_id>', methods=['DELETE'])
@jwt_required()
@tenant_required
def delete_prescription(prescription_id):
    """Delete prescription"""
    tenant_id = g.tenant_id
    prescription = Prescription.query.filter_by(id=prescription_id, tenant_id=tenant_id).first_or_404()
    
    db.session.delete(prescription)
    db.session.commit()
    
    return jsonify({'message': 'Prescription deleted'}), 200


# ============= DASHBOARD/ANALYTICS ENDPOINTS =============

@bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@tenant_required
def dashboard_stats():
    """Get dashboard statistics"""
    tenant_id = g.tenant_id
    today = date.today()
    
    total_patients = Patient.query.filter_by(tenant_id=tenant_id).count()
    today_appointments = Appointment.query.filter_by(tenant_id=tenant_id, date=today).count()
    today_visits = Visit.query.filter_by(tenant_id=tenant_id, date=today).count()
    total_medicines = Medicine.query.filter_by(tenant_id=tenant_id).count()
    total_prescriptions = Prescription.query.filter_by(tenant_id=tenant_id).count()
    
    # Monthly patient growth (last 12 months)
    monthly_stats = db.session.query(
        func.strftime('%Y-%m', Patient.created_at).label('month'),
        func.count(Patient.id).label('count')
    ).filter(
        Patient.tenant_id == tenant_id
    ).group_by('month').order_by('month').limit(12).all()
    
    return jsonify({
        'total_patients': total_patients,
        'today_appointments': today_appointments,
        'today_visits': today_visits,
        'total_medicines': total_medicines,
        'total_prescriptions': total_prescriptions,
        'monthly_patient_growth': [{'month': m, 'count': c} for m, c in monthly_stats]
    }), 200


# ============= USER MANAGEMENT ENDPOINTS =============

@bp.route('/users', methods=['GET'])
@jwt_required()
@tenant_required
@role_required('super_admin', 'clinic_admin')
def list_users():
    """List users in tenant"""
    tenant_id = g.tenant_id
    users = User.query.filter_by(tenant_id=tenant_id).order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@bp.route('/users', methods=['POST'])
@jwt_required()
@tenant_required
@role_required('super_admin', 'clinic_admin')
def create_user():
    """Create a new user in tenant"""
    tenant_id = g.tenant_id
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password', 'full_name', 'role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    valid_roles = ['clinic_admin', 'doctor', 'nurse', 'receptionist', 'patient']
    if data['role'] not in valid_roles:
        return jsonify({'error': f'Invalid role. Must be one of: {valid_roles}'}), 400
    
    user = User(
        tenant_id=tenant_id,
        username=data['username'],
        email=data['email'],
        full_name=data['full_name'],
        role=data['role']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201


# ============= ERROR HANDLERS =============

@bp.errorhandler(404)
def api_not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@bp.errorhandler(500)
def api_internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500