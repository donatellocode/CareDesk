from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from app import db
from app.models import Prescription, PrescriptionItem, Patient, Medicine, Visit
from app.forms import PrescriptionForm
from datetime import date

bp = Blueprint('prescriptions', __name__, url_prefix='/prescriptions')


@bp.route('/')
def list():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = Prescription.query.order_by(Prescription.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('prescriptions/list.html', prescriptions=pagination)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    form = PrescriptionForm()
    patients = Patient.query.order_by(Patient.name).all()
    form.patient_id.choices = [(0, 'Select a patient...')] + [(p.id, p.name) for p in patients]
    
    medicines = Medicine.query.order_by(Medicine.name).all()
    visits = Visit.query.order_by(Visit.date.desc()).limit(100).all()
    form.visit_id.choices = [(0, 'None')] + [(v.id, f"{v.patient.name} - {v.date}") for v in visits]
    
    if request.method == 'POST':
        prescription = Prescription(
            patient_id=int(request.form['patient_id']),
            visit_id=int(request.form['visit_id']) if request.form.get('visit_id') and request.form['visit_id'] != '0' else None,
            date=date.fromisoformat(request.form['date'])
        )
        db.session.add(prescription)
        db.session.flush()
        
        medicine_ids = request.form.getlist('medicine_id')
        doses = request.form.getlist('dose')
        instructions_list = request.form.getlist('instructions')
        
        for i, med_id in enumerate(medicine_ids):
            if med_id:
                item = PrescriptionItem(
                    prescription_id=prescription.id,
                    medicine_id=int(med_id),
                    dose=doses[i] if i < len(doses) else '',
                    instructions=instructions_list[i] if i < len(instructions_list) else ''
                )
                db.session.add(item)
        
        db.session.commit()
        flash('Prescription created successfully!', 'success')
        return redirect(url_for('prescriptions.view', id=prescription.id))
    
    return render_template('prescriptions/new.html', 
                         form=form,
                         patients=patients, 
                         medicines=medicines,
                         visits=visits)


@bp.route('/<int:id>')
def view(id):
    prescription = Prescription.query.get_or_404(id)
    return render_template('prescriptions/view.html', prescription=prescription)


@bp.route('/<int:id>/print')
def print_view(id):
    prescription = Prescription.query.get_or_404(id)
    return render_template('prescriptions/print.html', prescription=prescription)


@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    prescription = Prescription.query.get_or_404(id)
    db.session.delete(prescription)
    db.session.commit()
    flash('Prescription deleted successfully!', 'success')
    return redirect(url_for('prescriptions.list'))


@bp.route('/api/list')
def api_list():
    prescriptions = Prescription.query.order_by(Prescription.date.desc()).limit(100).all()
    return jsonify([p.to_dict() for p in prescriptions])


@bp.route('/api/<int:id>')
def api_get(id):
    prescription = Prescription.query.get_or_404(id)
    return jsonify(prescription.to_dict())
