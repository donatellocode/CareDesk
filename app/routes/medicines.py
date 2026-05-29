from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Medicine
from app.forms import MedicineForm
from sqlalchemy import or_

bp = Blueprint('medicines', __name__, url_prefix='/medicines')


@bp.route('/')
@login_required
def list():
    tenant_id = current_user.tenant_id
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Medicine.query.filter_by(tenant_id=tenant_id)
    if search:
        query = query.filter(or_(Medicine.name.ilike(f'%{search}%'), Medicine.category.ilike(f'%{search}%')))
    
    medicines = query.order_by(Medicine.name).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('medicines/list.html', medicines=medicines, search=search)


@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    tenant_id = current_user.tenant_id
    form = MedicineForm()
    if form.validate_on_submit():
        medicine = Medicine(
            tenant_id=tenant_id,
            name=form.name.data,
            category=form.category.data,
            default_dose=form.default_dose.data,
            instructions=form.instructions.data
        )
        db.session.add(medicine)
        db.session.commit()
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('medicines.list'))
    return render_template('medicines/new.html', form=form)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    tenant_id = current_user.tenant_id
    medicine = Medicine.query.filter_by(id=id, tenant_id=tenant_id).first_or_404()
    form = MedicineForm(obj=medicine)
    if form.validate_on_submit():
        form.populate_obj(medicine)
        db.session.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('medicines.list'))
    return render_template('medicines/edit.html', form=form, medicine=medicine)


@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    tenant_id = current_user.tenant_id
    medicine = Medicine.query.filter_by(id=id, tenant_id=tenant_id).first_or_404()
    db.session.delete(medicine)
    db.session.commit()
    flash('Medicine deleted successfully!', 'success')
    return redirect(url_for('medicines.list'))


@bp.route('/api/list')
def api_list():
    # Legacy endpoint - use /api/v1/medicines instead
    medicines = Medicine.query.order_by(Medicine.name).all()
    return jsonify([m.to_dict() for m in medicines])


@bp.route('/api/<int:id>')
def api_get(id):
    # Legacy endpoint - use /api/v1/medicines/<id> instead
    medicine = Medicine.query.get_or_404(id)
    return jsonify(medicine.to_dict())
