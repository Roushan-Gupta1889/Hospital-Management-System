from flask import Blueprint, request, jsonify
from app import db
from app.models import Appointment, Patient, Doctor
from app.utils import role_required, get_current_user, cache_clear_pattern
from datetime import datetime

bp = Blueprint('appointments', __name__, url_prefix='/api/appointments')

@bp.route('', methods=['POST'])
@role_required('patient')
def book_appointment():
    """Book a new appointment"""
    user = get_current_user()
    patient = user.patient_profile

    if not patient:
        return jsonify({'error': 'Patient profile not found'}), 404

    data = request.get_json()

    required_fields = ['doctor_id', 'appointment_date', 'appointment_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        # Validate doctor exists and is active
        doctor = Doctor.query.get(data['doctor_id'])
        if not doctor or not doctor.user.is_active:
            return jsonify({'error': 'Doctor not found or inactive'}), 404

        # Parse date and time
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()

        # Check for conflicts - prevent double booking for same doctor at same time
        existing = Appointment.query.filter(
            Appointment.doctor_id == data['doctor_id'],
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status == 'booked'
        ).first()

        if existing:
            return jsonify({
                'error': 'This time slot is already booked. Please choose another time.'
            }), 409

        # Create appointment
        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=data['doctor_id'],
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            reason=data.get('reason', ''),
            notes=data.get('notes', ''),
            status='booked'
        )

        db.session.add(appointment)
        db.session.commit()

        # Clear relevant caches
        cache_clear_pattern('appointments:*')
        cache_clear_pattern(f'patient:{patient.id}:*')
        cache_clear_pattern('admin:*')

        return jsonify({
            'message': 'Appointment booked successfully',
            'appointment': appointment.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:appointment_id>', methods=['GET'])
@role_required('patient', 'doctor', 'admin')
def get_appointment(appointment_id):
    """Get appointment details"""
    user = get_current_user()
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    # Check authorization
    if user.role == 'patient':
        if appointment.patient.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403
    elif user.role == 'doctor':
        if appointment.doctor.user_id != user.id:
            return jsonify({'error': 'Unauthorized'}), 403

    app_data = appointment.to_dict()
    if appointment.treatment:
        app_data['treatment'] = appointment.treatment.to_dict()

    return jsonify(app_data), 200

@bp.route('/<int:appointment_id>', methods=['PUT'])
@role_required('patient')
def reschedule_appointment(appointment_id):
    """Reschedule an appointment"""
    user = get_current_user()
    patient = user.patient_profile

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    if appointment.patient_id != patient.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if appointment.status != 'booked':
        return jsonify({'error': 'Can only reschedule booked appointments'}), 400

    data = request.get_json()

    try:
        # Parse new date and time
        if 'appointment_date' in data:
            new_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        else:
            new_date = appointment.appointment_date

        if 'appointment_time' in data:
            new_time = datetime.strptime(data['appointment_time'], '%H:%M').time()
        else:
            new_time = appointment.appointment_time

        # Check for conflicts
        existing = Appointment.query.filter(
            Appointment.id != appointment_id,
            Appointment.doctor_id == appointment.doctor_id,
            Appointment.appointment_date == new_date,
            Appointment.appointment_time == new_time,
            Appointment.status == 'booked'
        ).first()

        if existing:
            return jsonify({
                'error': 'This time slot is already booked. Please choose another time.'
            }), 409

        # Update appointment
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time

        if 'reason' in data:
            appointment.reason = data['reason']
        if 'notes' in data:
            appointment.notes = data['notes']

        db.session.commit()

        # Clear caches
        cache_clear_pattern('appointments:*')
        cache_clear_pattern(f'patient:{patient.id}:*')

        return jsonify({
            'message': 'Appointment rescheduled successfully',
            'appointment': appointment.to_dict()
        }), 200

    except ValueError as e:
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:appointment_id>', methods=['DELETE'])
@role_required('patient')
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    user = get_current_user()
    patient = user.patient_profile

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    if appointment.patient_id != patient.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if appointment.status != 'booked':
        return jsonify({'error': 'Can only cancel booked appointments'}), 400

    try:
        appointment.status = 'cancelled'
        db.session.commit()

        # Clear caches
        cache_clear_pattern('appointments:*')
        cache_clear_pattern(f'patient:{patient.id}:*')
        cache_clear_pattern('admin:*')

        return jsonify({
            'message': 'Appointment cancelled successfully',
            'appointment': appointment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/check-availability', methods=['POST'])
@role_required('patient')
def check_availability():
    """Check if a time slot is available"""
    data = request.get_json()

    required_fields = ['doctor_id', 'appointment_date', 'appointment_time']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        appointment_date = datetime.strptime(data['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(data['appointment_time'], '%H:%M').time()

        existing = Appointment.query.filter(
            Appointment.doctor_id == data['doctor_id'],
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status == 'booked'
        ).first()

        return jsonify({
            'available': existing is None
        }), 200

    except ValueError:
        return jsonify({'error': 'Invalid date or time format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
