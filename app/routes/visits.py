from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Visit, Patient, Appointment
from app.forms import VisitForm
from datetime import date

bp = Blueprint('visits', __name__, url_prefix='/visits')


@bp.route('/')
@login_required
def list():
    tenant_id = current_user.tenant_id
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = Visit.query.filter_by(tenant_id=tenant_id).order_by(Visit.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('visits/list.html', visits=pagination)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    tenant_id = current_user.tenant_id
    form = VisitForm()
    patients = Patient.query.filter_by(tenant_id=tenant_id).order_by(Patient.name).all()
    form.patient_id.choices = [(0, 'Select a patient...')] + [(p.id, p.name) for p in patients]
    
    appointments = Appointment.query.filter_by(tenant_id=tenant_id, status='waiting').order_by(Appointment.date.desc(), Appointment.time).all()
    form.appointment_id.choices = [(0, 'None')] + [(a.id, f"{a.patient.name} - {a.date} {a.time}") for a in appointments]
    
    today_date = date.today()
    
    if form.validate_on_submit():
        visit = Visit(
            tenant_id=tenant_id,
            patient_id=form.patient_id.data,
            appointment_id=form.appointment_id.data if form.appointment_id.data else None,
            diagnosis=form.diagnosis.data,
            notes=form.notes.data,
            date=form.date.data
        )
        
        if form.appointment_id.data and form.appointment_id.data != 0:
            appointment = Appointment.query.get(form.appointment_id.data)
            if appointment:
                appointment.status = 'completed'
        
        db.session.add(visit)
        db.session.commit()
        flash('Visit recorded successfully!', 'success')
        return redirect(url_for('visits.view', id=visit.id))
    return render_template('visits/new.html', form=form, patients=patients, appointments=appointments, today=today_date.strftime('%Y-%m-%d'))


@bp.route('/<int:id>')
@login_required
def view(id):
    tenant_id = current_user.tenant_id
    visit = Visit.query.filter_by(id=id, tenant_id=tenant_id).first_or_404()
    return render_template('visits/view.html', visit=visit)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    tenant_id = current_user.tenant_id
    visit = Visit.query.filter_by(id=id, tenant_id=tenant_id).first_or_404()
    form = VisitForm(obj=visit)
    if form.validate_on_submit():
        form.populate_obj(visit)
        db.session.commit()
        flash('Visit updated successfully!', 'success')
        return redirect(url_for('visits.view', id=visit.id))
    return render_template('visits/edit.html', form=form, visit=visit)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    tenant_id = current_user.tenant_id
    visit = Visit.query.filter_by(id=id, tenant_id=tenant_id).first_or_404()
    db.session.delete(visit)
    db.session.commit()
    flash('Visit deleted successfully!', 'success')
    return redirect(url_for('visits.list'))


@bp.route('/api/list')
def api_list():
    # Legacy endpoint - use /api/v1/visits instead
    visits = Visit.query.order_by(Visit.date.desc()).limit(100).all()
    return jsonify([v.to_dict() for v in visits])


@bp.route('/api/<int:id>')
def api_get(id):
    # Legacy endpoint - use /api/v1/visits/<id> instead
    visit = Visit.query.get_or_404(id)
    return jsonify(visit.to_dict())
