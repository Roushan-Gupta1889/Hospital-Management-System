from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import redis
import os

db = SQLAlchemy()
migrate = Migrate()
redis_client = None

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Redis configuration
    app.config['REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, supports_credentials=True, origins=['http://localhost:3000'])

    # Initialize Redis
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL'])

    # Register blueprints
    from app.routes import auth, admin, doctor, patient, appointments
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(doctor.bp)
    app.register_blueprint(patient.bp)
    app.register_blueprint(appointments.bp)

    # Create database tables and admin user
    with app.app_context():
        db.create_all()
        from app.models import User

        # Create admin if doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@hospital.com',
                role='admin',
                full_name='Hospital Administrator'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created: username='admin', password='admin123'")

    return app
