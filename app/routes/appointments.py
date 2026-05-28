from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Appointment, Patient
from datetime import datetime, date

bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@bp.route('/')
def list():
    selected_date = request.args.get('date')
    if selected_date:
        appointment_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        appointments = Appointment.query.filter_by(date=appointment_date)\
            .order_by(Appointment.time).all()
    else:
        appointments = Appointment.query.filter_by(date=date.today())\
            .order_by(Appointment.time).all()
        selected_date = date.today().strftime('%Y-%m-%d')
    return render_template('appointments/list.html', 
                         appointments=appointments, 
                         selected_date=selected_date)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    patients = Patient.query.order_by(Patient.name).all()
    if request.method == 'POST':
        appointment = Appointment(
            patient_id=int(request.form['patient_id']),
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
            time=request.form['time'],
            status='waiting'
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointments.list'))
    return render_template('appointments/new.html', patients=patients)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    appointment = Appointment.query.get_or_404(id)
    patients = Patient.query.order_by(Patient.name).all()
    if request.method == 'POST':
        appointment.patient_id = int(request.form['patient_id'])
        appointment.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        appointment.time = request.form['time']
        appointment.status = request.form['status']
        db.session.commit()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointments.list'))
    return render_template('appointments/edit.html', 
                         appointment=appointment, 
                         patients=patients)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment cancelled successfully!', 'success')
    return redirect(url_for('appointments.list'))

@bp.route('/<int:id>/status/<string:status>')
def update_status(id, status):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = status
    db.session.commit()
    flash(f'Appointment marked as {status}!', 'success')
    return redirect(url_for('appointments.list'))
