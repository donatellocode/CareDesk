from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Patient
from datetime import datetime

bp = Blueprint('patients', __name__, url_prefix='/patients')

@bp.route('/')
def list():
    search = request.args.get('search', '')
    if search:
        patients = Patient.query.filter(
            (Patient.name.like(f'%{search}%')) | 
            (Patient.phone.like(f'%{search}%'))
        ).order_by(Patient.name).all()
    else:
        patients = Patient.query.order_by(Patient.name).all()
    return render_template('patients/list.html', patients=patients, search=search)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        patient = Patient(
            name=request.form['name'],
            age=int(request.form['age']) if request.form['age'] else None,
            phone=request.form.get('phone', ''),
            gender=request.form.get('gender', ''),
            notes=request.form.get('notes', '')
        )
        db.session.add(patient)
        db.session.commit()
        flash('Patient created successfully!', 'success')
        return redirect(url_for('patients.list'))
    return render_template('patients/new.html')

@bp.route('/<int:id>')
def view(id):
    patient = Patient.query.get_or_404(id)
    return render_template('patients/view.html', patient=patient)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        patient.name = request.form['name']
        patient.age = int(request.form['age']) if request.form['age'] else None
        patient.phone = request.form.get('phone', '')
        patient.gender = request.form.get('gender', '')
        patient.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('patients.view', id=patient.id))
    return render_template('patients/edit.html', patient=patient)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    flash('Patient deleted successfully!', 'success')
    return redirect(url_for('patients.list'))
