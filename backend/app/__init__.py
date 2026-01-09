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

    # Configuration - use environment variables in production
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///hospital.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Redis configuration - optional
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    app.config['REDIS_URL'] = redis_url
    app.config['CELERY_BROKER_URL'] = redis_url
    app.config['CELERY_RESULT_BACKEND'] = redis_url

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # CORS - allow frontend URL from environment or localhost for development
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    CORS(app, supports_credentials=True, origins=[frontend_url, 'http://localhost:3000'])

    # Initialize Redis - make it optional
    global redis_client
    try:
        redis_client = redis.from_url(app.config['REDIS_URL'])
        redis_client.ping()  # Test connection
        print("✓ Redis connected successfully")
    except Exception as e:
        print(f"⚠ Redis not available: {e}")
        print("⚠ Background jobs (reminders, reports, CSV export) will be disabled")
        redis_client = None


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
