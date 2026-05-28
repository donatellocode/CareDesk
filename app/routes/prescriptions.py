from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Prescription, PrescriptionItem, Patient, Medicine, Visit
from datetime import datetime, date

bp = Blueprint('prescriptions', __name__, url_prefix='/prescriptions')

@bp.route('/')
def list():
    prescriptions = Prescription.query.order_by(Prescription.date.desc()).limit(50).all()
    return render_template('prescriptions/list.html', prescriptions=prescriptions)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    patients = Patient.query.order_by(Patient.name).all()
    medicines = Medicine.query.order_by(Medicine.name).all()
    visits = Visit.query.order_by(Visit.date.desc()).limit(100).all()
    
    if request.method == 'POST':
        prescription = Prescription(
            patient_id=int(request.form['patient_id']),
            visit_id=int(request.form['visit_id']) if request.form.get('visit_id') else None,
            date=datetime.strptime(request.form['date'], '%Y-%m-%d').date()
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
                         patients=patients, 
                         medicines=medicines,
                         visits=visits)

@bp.route('/<int:id>')
def view(id):
    prescription = Prescription.query.get_or_404(id)
    return render_template('prescriptions/view.html', prescription=prescription)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    prescription = Prescription.query.get_or_404(id)
    db.session.delete(prescription)
    db.session.commit()
    flash('Prescription deleted successfully!', 'success')
    return redirect(url_for('prescriptions.list'))
