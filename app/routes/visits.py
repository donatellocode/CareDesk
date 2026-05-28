from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from app import db
from app.models import Visit, Patient, Appointment
from app.forms import VisitForm

bp = Blueprint('visits', __name__, url_prefix='/visits')


@bp.route('/')
def list():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = Visit.query.order_by(Visit.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('visits/list.html', visits=pagination)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = VisitForm()
    patients = Patient.query.order_by(Patient.name).all()
    form.patient_id.choices = [(0, 'Select a patient...')] + [(p.id, p.name) for p in patients]
    
    appointments = Appointment.query.filter_by(status='waiting').order_by(Appointment.date.desc()).all()
    form.appointment_id.choices = [(0, 'None')] + [(a.id, f"{a.patient.name} - {a.date} {a.time}") for a in appointments]
    
    if form.validate_on_submit():
        visit = Visit(
            patient_id=form.patient_id.data,
            appointment_id=form.appointment_id.data if form.appointment_id.data else None,
            diagnosis=form.diagnosis.data,
            notes=form.notes.data,
            date=form.date.data
        )
        
        if form.appointment_id.data:
            appointment = Appointment.query.get(form.appointment_id.data)
            if appointment:
                appointment.status = 'completed'
        
        db.session.add(visit)
        db.session.commit()
        flash('Visit recorded successfully!', 'success')
        return redirect(url_for('visits.view', id=visit.id))
    return render_template('visits/new.html', form=form, patients=patients)


@bp.route('/<int:id>')
def view(id):
    visit = Visit.query.get_or_404(id)
    return render_template('visits/view.html', visit=visit)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    visit = Visit.query.get_or_404(id)
    form = VisitForm(obj=visit)
    if form.validate_on_submit():
        form.populate_obj(visit)
        db.session.commit()
        flash('Visit updated successfully!', 'success')
        return redirect(url_for('visits.view', id=visit.id))
    return render_template('visits/edit.html', form=form, visit=visit)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    visit = Visit.query.get_or_404(id)
    db.session.delete(visit)
    db.session.commit()
    flash('Visit deleted successfully!', 'success')
    return redirect(url_for('visits.list'))


@bp.route('/api/list')
def api_list():
    visits = Visit.query.order_by(Visit.date.desc()).limit(100).all()
    return jsonify([v.to_dict() for v in visits])


@bp.route('/api/<int:id>')
def api_get(id):
    visit = Visit.query.get_or_404(id)
    return jsonify(visit.to_dict())
