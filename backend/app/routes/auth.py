from flask import Blueprint, request, jsonify, session
from app import db
from app.models import User, Patient, Doctor
from app.utils import login_required, get_current_user

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """Register a new patient"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['username', 'email', 'password', 'full_name', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Check if username or email already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    try:
        # Create user with patient role
        user = User(
            username=data['username'],
            email=data['email'],
            role='patient',
            full_name=data['full_name'],
            phone=data.get('phone')
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()  # Get user.id before creating patient

        # Create patient profile
        patient = Patient(
            user_id=user.id,
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender'),
            address=data.get('address'),
            blood_group=data.get('blood_group'),
            emergency_contact=data.get('emergency_contact')
        )
        db.session.add(patient)
        db.session.commit()

        return jsonify({
            'message': 'Patient registered successfully',
            'user': user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/login', methods=['POST'])
def login():
    """Login for all user types"""
    data = request.get_json()

    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 403

    # Set session
    session['user_id'] = user.id
    session['role'] = user.role

    response_data = {
        'message': 'Login successful',
        'user': user.to_dict()
    }

    # Add profile data based on role
    if user.role == 'doctor' and user.doctor_profile:
        response_data['profile'] = user.doctor_profile.to_dict()
    elif user.role == 'patient' and user.patient_profile:
        response_data['profile'] = user.patient_profile.to_dict()

    return jsonify(response_data), 200

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout current user"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/me', methods=['GET'])
@login_required
def get_me():
    """Get current user info"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    response_data = {'user': user.to_dict()}

    # Add profile data based on role
    if user.role == 'doctor' and user.doctor_profile:
        response_data['profile'] = user.doctor_profile.to_dict()
    elif user.role == 'patient' and user.patient_profile:
        response_data['profile'] = user.patient_profile.to_dict()

    return jsonify(response_data), 200

@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    data = request.get_json()
    user = get_current_user()

    if not user.check_password(data.get('old_password', '')):
        return jsonify({'error': 'Invalid current password'}), 400

    if not data.get('new_password'):
        return jsonify({'error': 'New password required'}), 400

    try:
        user.set_password(data['new_password'])
        db.session.commit()
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
