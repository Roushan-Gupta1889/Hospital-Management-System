from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Doctor, Patient, Appointment, Department
from app.utils import role_required, cache_get, cache_set, cache_delete, cache_clear_pattern
from datetime import datetime

bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def dashboard():
    """Get admin dashboard statistics"""
    cache_key = 'admin:dashboard'
    cached_data = cache_get(cache_key)

    if cached_data:
        return jsonify(cached_data), 200

    try:
        total_doctors = Doctor.query.join(User).filter(User.is_active == True).count()
        total_patients = Patient.query.join(User).filter(User.is_active == True).count()
        total_appointments = Appointment.query.count()
        pending_appointments = Appointment.query.filter_by(status='booked').count()
        completed_appointments = Appointment.query.filter_by(status='completed').count()
        cancelled_appointments = Appointment.query.filter_by(status='cancelled').count()

        data = {
            'total_doctors': total_doctors,
            'total_patients': total_patients,
            'total_appointments': total_appointments,
            'pending_appointments': pending_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments
        }

        # Cache for 5 minutes
        cache_set(cache_key, data, 300)

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Department Management
@bp.route('/departments', methods=['GET', 'POST'])
@role_required('admin')
def manage_departments():
    if request.method == 'GET':
        departments = Department.query.all()
        return jsonify([dept.to_dict() for dept in departments]), 200

    elif request.method == 'POST':
        data = request.get_json()

        if not data.get('name'):
            return jsonify({'error': 'Department name is required'}), 400

        if Department.query.filter_by(name=data['name']).first():
            return jsonify({'error': 'Department already exists'}), 400

        try:
            department = Department(
                name=data['name'],
                description=data.get('description')
            )
            db.session.add(department)
            db.session.commit()

            cache_clear_pattern('departments:*')

            return jsonify({
                'message': 'Department created successfully',
                'department': department.to_dict()
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# Doctor Management
@bp.route('/doctors', methods=['GET'])
@role_required('admin')
def get_doctors():
    """Get all doctors"""
    try:
        search = request.args.get('search', '')
        department_id = request.args.get('department_id')

        query = Doctor.query.join(User)

        if search:
            query = query.filter(
                (User.full_name.ilike(f'%{search}%')) |
                (Doctor.specialization.ilike(f'%{search}%'))
            )

        if department_id:
            query = query.filter(Doctor.department_id == department_id)

        doctors = query.all()
        return jsonify([doctor.to_dict() for doctor in doctors]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/doctors', methods=['POST'])
@role_required('admin')
def create_doctor():
    """Create a new doctor"""
    data = request.get_json()

    required_fields = ['username', 'email', 'password', 'full_name', 'specialization']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    try:
        # Create user
        user = User(
            username=data['username'],
            email=data['email'],
            role='doctor',
            full_name=data['full_name'],
            phone=data.get('phone')
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()

        # Create doctor profile
        doctor = Doctor(
            user_id=user.id,
            department_id=data.get('department_id'),
            specialization=data['specialization'],
            qualification=data.get('qualification'),
            experience_years=data.get('experience_years'),
            consultation_fee=data.get('consultation_fee')
        )
        db.session.add(doctor)
        db.session.commit()

        cache_clear_pattern('admin:*')
        cache_clear_pattern('doctors:*')

        return jsonify({
            'message': 'Doctor created successfully',
            'doctor': doctor.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/doctors/<int:doctor_id>', methods=['GET', 'PUT', 'DELETE'])
@role_required('admin')
def manage_doctor(doctor_id):
    """Get, update or delete a doctor"""
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'error': 'Doctor not found'}), 404

    if request.method == 'GET':
        return jsonify(doctor.to_dict()), 200

    elif request.method == 'PUT':
        data = request.get_json()

        try:
            # Update user info
            if 'full_name' in data:
                doctor.user.full_name = data['full_name']
            if 'email' in data:
                doctor.user.email = data['email']
            if 'phone' in data:
                doctor.user.phone = data['phone']

            # Update doctor info
            if 'department_id' in data:
                doctor.department_id = data['department_id']
            if 'specialization' in data:
                doctor.specialization = data['specialization']
            if 'qualification' in data:
                doctor.qualification = data['qualification']
            if 'experience_years' in data:
                doctor.experience_years = data['experience_years']
            if 'consultation_fee' in data:
                doctor.consultation_fee = data['consultation_fee']

            db.session.commit()

            cache_clear_pattern('admin:*')
            cache_clear_pattern('doctors:*')

            return jsonify({
                'message': 'Doctor updated successfully',
                'doctor': doctor.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    elif request.method == 'DELETE':
        try:
            doctor.user.is_active = False
            db.session.commit()

            cache_clear_pattern('admin:*')
            cache_clear_pattern('doctors:*')

            return jsonify({'message': 'Doctor deactivated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# Patient Management
@bp.route('/patients', methods=['GET'])
@role_required('admin')
def get_patients():
    """Get all patients"""
    try:
        search = request.args.get('search', '')

        query = Patient.query.join(User)

        if search:
            query = query.filter(
                (User.full_name.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%')) |
                (User.phone.ilike(f'%{search}%'))
            )

        patients = query.all()
        return jsonify([patient.to_dict() for patient in patients]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/patients/<int:patient_id>', methods=['GET', 'PUT', 'DELETE'])
@role_required('admin')
def manage_patient(patient_id):
    """Get, update or delete a patient"""
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404

    if request.method == 'GET':
        return jsonify(patient.to_dict()), 200

    elif request.method == 'PUT':
        data = request.get_json()

        try:
            # Update user info
            if 'full_name' in data:
                patient.user.full_name = data['full_name']
            if 'email' in data:
                patient.user.email = data['email']
            if 'phone' in data:
                patient.user.phone = data['phone']

            # Update patient info
            if 'date_of_birth' in data:
                patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            if 'gender' in data:
                patient.gender = data['gender']
            if 'address' in data:
                patient.address = data['address']
            if 'blood_group' in data:
                patient.blood_group = data['blood_group']
            if 'emergency_contact' in data:
                patient.emergency_contact = data['emergency_contact']
            if 'medical_history' in data:
                patient.medical_history = data['medical_history']

            db.session.commit()

            cache_clear_pattern('admin:*')

            return jsonify({
                'message': 'Patient updated successfully',
                'patient': patient.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    elif request.method == 'DELETE':
        try:
            patient.user.is_active = False
            db.session.commit()

            cache_clear_pattern('admin:*')

            return jsonify({'message': 'Patient deactivated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

# Appointment Management
@bp.route('/appointments', methods=['GET'])
@role_required('admin')
def get_all_appointments():
    """Get all appointments"""
    try:
        status = request.args.get('status')

        query = Appointment.query

        if status:
            query = query.filter_by(status=status)

        appointments = query.order_by(Appointment.appointment_date.desc()).all()
        return jsonify([appointment.to_dict() for appointment in appointments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
