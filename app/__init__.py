import logging
import os
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    
    # Import Flask-Migrate only in production or when needed
    if config_name != 'testing':
        from flask_migrate import Migrate
        migrate = Migrate()
        migrate.init_app(app, db)
    
    from app.routes import patients, appointments, visits, medicines, prescriptions, home
    app.register_blueprint(patients.bp)
    app.register_blueprint(appointments.bp)
    app.register_blueprint(visits.bp)
    app.register_blueprint(medicines.bp)
    app.register_blueprint(prescriptions.bp)
    app.register_blueprint(home.bp)
    
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
