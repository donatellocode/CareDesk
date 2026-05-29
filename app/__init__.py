import logging
import os
from datetime import timedelta
from flask import Flask, jsonify, render_template, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Get the base directory (parent of app folder)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure instance directory exists
    instance_path = os.path.join(base_dir, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print(f"Created instance directory: {instance_path}")
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Debug: print actual DB path being used
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    print(f"Database URI: {db_uri}")
    print(f"Instance path: {instance_path}")
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    # Initialize JWT
    jwt.init_app(app)
    
    # JWT additional claims loader
    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        from app.models import User
        user = User.query.get(int(identity))
        if user:
            return {
                'tenant_id': user.tenant_id,
                'role': user.role,
                'full_name': user.full_name
            }
        return {'tenant_id': 0, 'role': 'guest'}
    
    # Create all database tables - MUST import models first
    with app.app_context():
        from app.models import Patient, Appointment, Visit, Medicine, Prescription, PrescriptionItem, User, Tenant
        db.create_all()
        print("Database tables created/verified")
        
        # Create default tenant if not exists
        default_tenant = Tenant.query.filter_by(slug='default').first()
        if not default_tenant:
            default_tenant = Tenant(
                name='Default Clinic',
                slug='default',
                subscription_plan='free'
            )
            db.session.add(default_tenant)
            db.session.commit()
            print("Default tenant created")
        
        # Create default super admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@caredesk.com',
                full_name='System Admin',
                role='super_admin',
                tenant_id=default_tenant.id
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created (username: admin, password: admin123)")
        
        # Create default clinic admin user if not exists
        if not User.query.filter_by(username='clinic_admin').first():
            clinic_admin = User(
                username='clinic_admin',
                email='clinic@caredesk.com',
                full_name='Clinic Admin',
                role='clinic_admin',
                tenant_id=default_tenant.id
            )
            clinic_admin.set_password('clinic123')
            db.session.add(clinic_admin)
            db.session.commit()
            print("Default clinic admin user created")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
    
    # Import Flask-Migrate only in production or when needed
    if config_name != 'testing':
        from flask_migrate import Migrate
        migrate = Migrate()
        migrate.init_app(app, db)
    
    from app.routes import patients, appointments, visits, medicines, prescriptions, home, auth, api
    app.register_blueprint(patients.bp)
    app.register_blueprint(appointments.bp)
    app.register_blueprint(visits.bp)
    app.register_blueprint(medicines.bp)
    app.register_blueprint(prescriptions.bp)
    app.register_blueprint(home.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(api.bp)  # API v1 blueprint
    
    setup_logging(app)
    register_error_handlers(app)
    register_shell_context(app)
    
    return app


def setup_logging(app):
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/caredesk.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('CareDesk startup')


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(error):
        if request_wants_json():
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request_wants_json():
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        if request_wants_json():
            return jsonify({'error': 'Forbidden'}), 403
    
    @app.errorhandler(400)
    def bad_request_error(error):
        if request_wants_json():
            return jsonify({'error': 'Bad request'}), 400


def request_wants_json():
    from flask import request
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > request.accept_mimetypes['text/html']


def register_shell_context(app):
    from app import models
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'Patient': models.Patient, 
                'Appointment': models.Appointment, 'Visit': models.Visit,
                'Medicine': models.Medicine, 'Prescription': models.Prescription}
