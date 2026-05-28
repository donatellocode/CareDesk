from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Appointment, Patient
from app.forms import AppointmentForm
from datetime import date

bp = Blueprint('appointments', __name__, url_prefix='/appointments')


@bp.route('/')
@login_required
def list():
    selected_date = request.args.get('date')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    if selected_date:
        from datetime import datetime
        appointment_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        pagination = Appointment.query.filter_by(date=appointment_date)\
            .order_by(Appointment.time).paginate(page=page, per_page=per_page, error_out=False)
    else:
        pagination = Appointment.query.filter_by(date=date.today())\
            .order_by(Appointment.time).paginate(page=page, per_page=per_page, error_out=False)
        selected_date = date.today().strftime('%Y-%m-%d')
    
    return render_template('appointments/list.html', 
                         appointments=pagination, 
                         selected_date=selected_date)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = AppointmentForm()
    patients = Patient.query.order_by(Patient.name).all()
    form.patient_id.choices = [(0, 'Select a patient...')] + [(p.id, p.name) for p in patients]
    
    if form.validate_on_submit():
        appointment = Appointment(
            patient_id=form.patient_id.data,
            date=form.date.data,
            time=form.time.data,
            status=form.status.data,
            notes=form.notes.data
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('appointments.list'))
    return render_template('appointments/new.html', form=form, patients=patients)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    appointment = Appointment.query.get_or_404(id)
    form = AppointmentForm(obj=appointment)
    patients = Patient.query.order_by(Patient.name).all()
    form.patient_id.choices = [(p.id, p.name) for p in patients]
    
    if form.validate_on_submit():
        form.populate_obj(appointment)
        db.session.commit()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointments.list'))
    return render_template('appointments/edit.html', form=form, appointment=appointment)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    appointment = Appointment.query.get_or_404(id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Appointment cancelled successfully!', 'success')
    return redirect(url_for('appointments.list'))


@bp.route('/<int:id>/status/<string:status>')
@login_required
def update_status(id, status):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = status
    db.session.commit()
    flash(f'Appointment marked as {status}!', 'success')
    return redirect(url_for('appointments.list'))


@bp.route('/api/list')
def api_list():
    appointments = Appointment.query.order_by(Appointment.date.desc(), Appointment.time).limit(100).all()
    return jsonify([a.to_dict() for a in appointments])


@bp.route('/api/<int:id>')
def api_get(id):
    appointment = Appointment.query.get_or_404(id)
    return jsonify(appointment.to_dict())
