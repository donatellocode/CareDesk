from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Medicine

bp = Blueprint('medicines', __name__, url_prefix='/medicines')

@bp.route('/')
def list():
    search = request.args.get('search', '')
    if search:
        medicines = Medicine.query.filter(
            (Medicine.name.like(f'%{search}%')) |
            (Medicine.category.like(f'%{search}%'))
        ).order_by(Medicine.name).all()
    else:
        medicines = Medicine.query.order_by(Medicine.name).all()
    return render_template('medicines/list.html', medicines=medicines, search=search)

@bp.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        medicine = Medicine(
            name=request.form['name'],
            category=request.form.get('category', ''),
            default_dose=request.form.get('default_dose', ''),
            instructions=request.form.get('instructions', '')
        )
        db.session.add(medicine)
        db.session.commit()
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('medicines.list'))
    return render_template('medicines/new.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    medicine = Medicine.query.get_or_404(id)
    if request.method == 'POST':
        medicine.name = request.form['name']
        medicine.category = request.form.get('category', '')
        medicine.default_dose = request.form.get('default_dose', '')
        medicine.instructions = request.form.get('instructions', '')
        db.session.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('medicines.list'))
    return render_template('medicines/edit.html', medicine=medicine)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    medicine = Medicine.query.get_or_404(id)
    db.session.delete(medicine)
    db.session.commit()
    flash('Medicine deleted successfully!', 'success')
    return redirect(url_for('medicines.list'))
