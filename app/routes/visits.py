from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Visit, Patient, Appointment
from datetime import datetime, date

bp = Blueprint('visits', __name__, url_prefix='/visits')

@bp.route('/')
def list():
    visits = Visit.query.order_by(Visit.date.desc()).limit(50).all()
    return render_template('visits/list.html', visits=visits)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    patients = Patient.query.order_by(Patient.name).all()
    if request.method == 'POST':
        patient_id = int(request.form['patient_id'])
        appointment_id = request.form.get('appointment_id')
        
        visit = Visit(
            patient_id=patient_id,
            appointment_id=int(appointment_id) if appointment_id else None,
            diagnosis=request.form.get('diagnosis', ''),
            notes=request.form.get('notes', ''),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        )
        
        if appointment_id:
            appointment = Appointment.query.get(int(appointment_id))
            if appointment:
                appointment.status = 'completed'
        
        db.session.add(visit)
        db.session.commit()
        flash('Visit recorded successfully!', 'success')
        return redirect(url_for('visits.view', id=visit.id))
    return render_template('visits/new.html', patients=patients)

@bp.route('/<int:id>')
def view(id):
    visit = Visit.query.get_or_404(id)
    return render_template('visits/view.html', visit=visit)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    visit = Visit.query.get_or_404(id)
    if request.method == 'POST':
        visit.diagnosis = request.form.get('diagnosis', '')
        visit.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Visit updated successfully!', 'success')
        return redirect(url_for('visits.view', id=visit.id))
    return render_template('visits/edit.html', visit=visit)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    visit = Visit.query.get_or_404(id)
    db.session.delete(visit)
    db.session.commit()
    flash('Visit deleted successfully!', 'success')
    return redirect(url_for('visits.list'))
