from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Patient
from app.forms import PatientForm
from sqlalchemy import or_

bp = Blueprint('patients', __name__, url_prefix='/patients')


@bp.route('/')
@login_required
def list():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Patient.query
    if search:
        query = query.filter(or_(Patient.name.ilike(f'%{search}%'), Patient.phone.ilike(f'%{search}%')))
    
    patients = query.order_by(Patient.name).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('patients/list.html', patients=patients, search=search)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = PatientForm()
    if form.validate_on_submit():
        patient = Patient(
            name=form.name.data,
            age=form.age.data,
            phone=form.phone.data,
            gender=form.gender.data,
            notes=form.notes.data
        )
        db.session.add(patient)
        db.session.commit()
        flash('Patient created successfully!', 'success')
        return redirect(url_for('patients.list'))
    return render_template('patients/new.html', form=form)


@bp.route('/<int:id>')
@login_required
def view(id):
    patient = Patient.query.get_or_404(id)
    return render_template('patients/view.html', patient=patient)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    patient = Patient.query.get_or_404(id)
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        form.populate_obj(patient)
        db.session.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('patients.view', id=patient.id))
    return render_template('patients/edit.html', form=form, patient=patient)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient deleted successfully!', 'success')
    return redirect(url_for('patients.list'))


@bp.route('/api/list')
def api_list():
    patients = Patient.query.order_by(Patient.name).all()
    return jsonify([p.to_dict() for p in patients])


@bp.route('/api/<int:id>')
def api_get(id):
    patient = Patient.query.get_or_404(id)
    return jsonify(patient.to_dict())
