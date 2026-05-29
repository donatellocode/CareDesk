from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Tenant
from functools import wraps
from datetime import datetime

bp = Blueprint('auth', __name__, url_prefix='/auth')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role not in ['super_admin', 'clinic_admin']:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated_function


def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        if current_user.role != 'super_admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home.index'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return render_template('auth/login.html')
        
        if not user.is_active:
            flash('Your account is inactive. Please contact administrator.', 'danger')
            return render_template('auth/login.html')
        
        login_user(user)
        user.last_login = db.func.now()
        db.session.commit()
        
        flash(f'Welcome back, {user.full_name}!', 'success')
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('home.index'))
    
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
@admin_required
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        role = request.form.get('role', 'doctor')
        
        if not all([username, email, password, full_name]):
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        
        user = User(
            username=username, 
            email=email, 
            full_name=full_name, 
            role=role,
            tenant_id=current_user.tenant_id
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {full_name} created successfully!', 'success')
        return redirect(url_for('auth.users'))
    
    return render_template('auth/register.html')


@bp.route('/users')
@admin_required
def users():
    all_users = User.query.filter_by(tenant_id=current_user.tenant_id).order_by(User.created_at.desc()).all()
    return render_template('auth/users.html', users=all_users)


@bp.route('/users/<int:id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'danger')
        return redirect(url_for('auth.users'))
    
    if user.tenant_id != current_user.tenant_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User {user.full_name} {"activated" if user.is_active else "deactivated"}.', 'success')
    return redirect(url_for('auth.users'))


@bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)


@bp.route('/profile', methods=['POST'])
@login_required
def profile_update():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    
    if not full_name or not email:
        flash('Name and email are required.', 'danger')
        return redirect(url_for('auth.profile'))
    
    current_user.full_name = full_name
    current_user.email = email
    db.session.commit()
    
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('auth.profile'))


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_password.html')
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/change_password.html')
        
        current_user.set_password(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html')