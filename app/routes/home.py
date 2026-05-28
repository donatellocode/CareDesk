from flask import Blueprint, render_template, request
from app import db
from app.models import Patient, Appointment, Visit, Medicine, Prescription
from sqlalchemy import func
from datetime import date

bp = Blueprint('home', __name__)

@bp.route('/')
def index():
    today = date.today()
    
    total_patients = Patient.query.count()
    today_appointments = Appointment.query.filter_by(date=today).count()
    today_visits = Visit.query.filter_by(date=today).count()
    total_medicines = Medicine.query.count()
    
    recent_appointments = Appointment.query.filter_by(date=today)\
        .order_by(Appointment.time).limit(5).all()
    
    return render_template('index.html', 
                         total_patients=total_patients,
                         today_appointments=today_appointments,
                         today_visits=today_visits,
                         total_medicines=total_medicines,
                         recent_appointments=recent_appointments)
