from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app import db
from app.models import Patient, Appointment, Visit, Medicine, Prescription
from sqlalchemy import func
from datetime import date

bp = Blueprint('home', __name__)

@bp.route('/')
@login_required
def index():
    today = date.today()
    
    # Filter by tenant for multi-tenant support
    tenant_id = current_user.tenant_id
    
    total_patients = Patient.query.filter_by(tenant_id=tenant_id).count()
    today_appointments = Appointment.query.filter_by(tenant_id=tenant_id, date=today).count()
    today_visits = Visit.query.filter_by(tenant_id=tenant_id, date=today).count()
    total_medicines = Medicine.query.filter_by(tenant_id=tenant_id).count()
    
    recent_appointments = Appointment.query.filter_by(tenant_id=tenant_id, date=today)\
        .order_by(Appointment.time).limit(5).all()
    
    return render_template('index.html', 
                         total_patients=total_patients,
                         today_appointments=today_appointments,
                         today_visits=today_visits,
                         total_medicines=total_medicines,
                         recent_appointments=recent_appointments)
