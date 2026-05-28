from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    from app.routes import patients, appointments, visits, medicines, prescriptions, home
    app.register_blueprint(patients.bp)
    app.register_blueprint(appointments.bp)
    app.register_blueprint(visits.bp)
    app.register_blueprint(medicines.bp)
    app.register_blueprint(prescriptions.bp)
    app.register_blueprint(home.bp)
    
    with app.app_context():
        from app import models
        db.create_all()
    
    return app
