from flask import Blueprint, request, jsonify
from app import db
from app.models import Patient, Doctor, Appointment, Department, DoctorAvailability
from app.utils import role_required, get_current_user, cache_get, cache_set, cache_clear_pattern
from app.tasks import export_patient_treatments_csv
from datetime import datetime, date, timedelta

bp = Blueprint('patient', __name__, url_prefix='/api/patient')

@bp.route('/dashboard', methods=['GET'])
@role_required('patient')
def dashboard():
    """Get patient dashboard data"""
    user = get_current_user()
    patient = user.patient_profile

    if not patient:
        return jsonify({'error': 'Patient profile not found'}), 404

    cache_key = f'patient:{patient.id}:dashboard'
    cached_data = cache_get(cache_key)

    if cached_data:
        return jsonify(cached_data), 200

    try:
        # Get all departments
        departments = Department.query.all()

        # Get upcoming appointments
        today = date.today()
        upcoming_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.appointment_date >= today,
            Appointment.status == 'booked'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()

        # Get recent appointment history
        past_appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status.in_(['completed', 'cancelled'])
        ).order_by(Appointment.appointment_date.desc()).limit(5).all()

        data = {
            'patient': patient.to_dict(),
            'departments': [dept.to_dict() for dept in departments],
            'upcoming_appointments': [app.to_dict() for app in upcoming_appointments],
            'recent_appointments': [app.to_dict() for app in past_appointments]
        }

        # Cache for 2 minutes
        cache_set(cache_key, data, 120)

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['GET', 'PUT'])
@role_required('patient')
def manage_profile():
    """Get or update patient profile"""
    user = get_current_user()
    patient = user.patient_profile

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

            cache_clear_pattern(f'patient:{patient.id}:*')

            return jsonify({
                'message': 'Profile updated successfully',
                'patient': patient.to_dict()
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@bp.route('/doctors', methods=['GET'])
@role_required('patient')
def search_doctors():
    """Search doctors by specialization or name"""
    try:
        search = request.args.get('search', '')
        specialization = request.args.get('specialization', '')
        department_id = request.args.get('department_id')

        cache_key = f'doctors:search:{search}:{specialization}:{department_id}'
        cached_data = cache_get(cache_key)

        if cached_data:
            return jsonify(cached_data), 200

        query = Doctor.query.join(Doctor.user).filter(Doctor.user.has(is_active=True))

        if search:
            query = query.filter(
                (Doctor.user.has(full_name=search)) |
                (Doctor.specialization.ilike(f'%{search}%'))
            )

        if specialization:
            query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))

        if department_id:
            query = query.filter(Doctor.department_id == department_id)

        doctors = query.all()
        result = []

        for doctor in doctors:
            doctor_data = doctor.to_dict()

            # Get availability for next 7 days
            today = date.today()
            next_week = today + timedelta(days=7)

            availabilities = DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor.id,
                DoctorAvailability.date >= today,
                DoctorAvailability.date <= next_week,
                DoctorAvailability.is_available == True
            ).all()

            doctor_data['availability'] = [avail.to_dict() for avail in availabilities]
            result.append(doctor_data)

        # Cache for 3 minutes
        cache_set(cache_key, result, 180)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/appointments', methods=['GET'])
@role_required('patient')
def get_appointments():
    """Get patient's appointments"""
    user = get_current_user()
    patient = user.patient_profile

    try:
        status = request.args.get('status')

        query = Appointment.query.filter_by(patient_id=patient.id)

        if status:
            query = query.filter_by(status=status)

        appointments = query.order_by(Appointment.appointment_date.desc()).all()

        result = []
        for appointment in appointments:
            app_data = appointment.to_dict()
            if appointment.treatment:
                app_data['treatment'] = appointment.treatment.to_dict()
            result.append(app_data)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/appointments/history', methods=['GET'])
@role_required('patient')
def get_appointment_history():
    """Get patient's appointment history with treatments"""
    user = get_current_user()
    patient = user.patient_profile

    cache_key = f'patient:{patient.id}:history'
    cached_data = cache_get(cache_key)

    if cached_data:
        return jsonify(cached_data), 200

    try:
        appointments = Appointment.query.filter(
            Appointment.patient_id == patient.id,
            Appointment.status == 'completed'
        ).order_by(Appointment.appointment_date.desc()).all()

        result = []
        for appointment in appointments:
            app_data = appointment.to_dict()
            if appointment.treatment:
                app_data['treatment'] = appointment.treatment.to_dict()
            result.append(app_data)

        # Cache for 5 minutes
        cache_set(cache_key, result, 300)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/export-treatments', methods=['POST'])
@role_required('patient')
def export_treatments():
    """Trigger async job to export treatment history as CSV"""
    user = get_current_user()
    patient = user.patient_profile

    try:
        # Trigger async Celery task
        task = export_patient_treatments_csv.delay(patient.id)

        return jsonify({
            'message': 'Export started. You will be notified when complete.',
            'task_id': task.id
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/export-status/<task_id>', methods=['GET'])
@role_required('patient')
def get_export_status(task_id):
    """Get status of CSV export task"""
    from celery.result import AsyncResult

    try:
        task = AsyncResult(task_id)

        if task.state == 'PENDING':
            response = {
                'status': 'pending',
                'message': 'Task is waiting to be processed'
            }
        elif task.state == 'SUCCESS':
            response = {
                'status': 'completed',
                'result': task.result
            }
        elif task.state == 'FAILURE':
            response = {
                'status': 'failed',
                'error': str(task.info)
            }
        else:
            response = {
                'status': task.state
            }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
