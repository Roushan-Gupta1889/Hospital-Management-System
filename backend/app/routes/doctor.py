from flask import Blueprint, request, jsonify
from app import db
from app.models import Doctor, Appointment, Treatment, DoctorAvailability
from app.utils import role_required, get_current_user, cache_clear_pattern
from datetime import datetime, timedelta, date

bp = Blueprint('doctor', __name__, url_prefix='/api/doctor')

@bp.route('/dashboard', methods=['GET'])
@role_required('doctor')
def dashboard():
    """Get doctor dashboard data"""
    user = get_current_user()
    doctor = user.doctor_profile

    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    try:
        # Get upcoming appointments for the next 7 days
        today = date.today()
        next_week = today + timedelta(days=7)

        upcoming_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date >= today,
            Appointment.appointment_date <= next_week,
            Appointment.status == 'booked'
        ).order_by(Appointment.appointment_date, Appointment.appointment_time).all()

        # Get today's appointments
        today_appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_date == today
        ).all()

        # Get patients assigned to doctor
        patients = db.session.query(Appointment.patient_id).filter(
            Appointment.doctor_id == doctor.id
        ).distinct().count()

        # Get statistics
        total_appointments = Appointment.query.filter_by(doctor_id=doctor.id).count()
        completed = Appointment.query.filter_by(doctor_id=doctor.id, status='completed').count()

        data = {
            'doctor': doctor.to_dict(),
            'upcoming_appointments': [app.to_dict() for app in upcoming_appointments],
            'today_appointments': [app.to_dict() for app in today_appointments],
            'total_patients': patients,
            'total_appointments': total_appointments,
            'completed_appointments': completed
        }

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/appointments', methods=['GET'])
@role_required('doctor')
def get_appointments():
    """Get doctor's appointments"""
    user = get_current_user()
    doctor = user.doctor_profile

    try:
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        query = Appointment.query.filter_by(doctor_id=doctor.id)

        if status:
            query = query.filter_by(status=status)

        if date_from:
            query = query.filter(Appointment.appointment_date >= datetime.strptime(date_from, '%Y-%m-%d').date())

        if date_to:
            query = query.filter(Appointment.appointment_date <= datetime.strptime(date_to, '%Y-%m-%d').date())

        appointments = query.order_by(Appointment.appointment_date.desc()).all()
        return jsonify([app.to_dict() for app in appointments]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/appointments/<int:appointment_id>/complete', methods=['POST'])
@role_required('doctor')
def complete_appointment(appointment_id):
    """Mark appointment as completed and add treatment"""
    user = get_current_user()
    doctor = user.doctor_profile

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    if appointment.doctor_id != doctor.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if not data.get('diagnosis'):
        return jsonify({'error': 'Diagnosis is required'}), 400

    try:
        # Update appointment status
        appointment.status = 'completed'

        # Create or update treatment
        if appointment.treatment:
            treatment = appointment.treatment
            treatment.diagnosis = data['diagnosis']
            treatment.prescription = data.get('prescription', '')
            treatment.treatment_notes = data.get('treatment_notes', '')
            if data.get('next_visit_date'):
                treatment.next_visit_date = datetime.strptime(data['next_visit_date'], '%Y-%m-%d').date()
        else:
            treatment = Treatment(
                appointment_id=appointment.id,
                diagnosis=data['diagnosis'],
                prescription=data.get('prescription', ''),
                treatment_notes=data.get('treatment_notes', ''),
                next_visit_date=datetime.strptime(data['next_visit_date'], '%Y-%m-%d').date() if data.get('next_visit_date') else None
            )
            db.session.add(treatment)

        db.session.commit()

        cache_clear_pattern('appointments:*')
        cache_clear_pattern('patient:*')

        return jsonify({
            'message': 'Appointment completed successfully',
            'appointment': appointment.to_dict(),
            'treatment': treatment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
@role_required('doctor')
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    user = get_current_user()
    doctor = user.doctor_profile

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    if appointment.doctor_id != doctor.id:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        appointment.status = 'cancelled'
        db.session.commit()

        cache_clear_pattern('appointments:*')

        return jsonify({
            'message': 'Appointment cancelled successfully',
            'appointment': appointment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@role_required('doctor')
def get_patient_history(patient_id):
    """Get patient's treatment history"""
    user = get_current_user()
    doctor = user.doctor_profile

    try:
        # Get all completed appointments for this patient with this doctor
        appointments = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.doctor_id == doctor.id,
            Appointment.status == 'completed'
        ).order_by(Appointment.appointment_date.desc()).all()

        history = []
        for appointment in appointments:
            app_data = appointment.to_dict()
            if appointment.treatment:
                app_data['treatment'] = appointment.treatment.to_dict()
            history.append(app_data)

        return jsonify(history), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Doctor Availability Management
@bp.route('/availability', methods=['GET', 'POST'])
@role_required('doctor')
def manage_availability():
    """Get or set doctor availability"""
    user = get_current_user()
    doctor = user.doctor_profile

    if request.method == 'GET':
        try:
            # Get availability for next 7 days
            today = date.today()
            next_week = today + timedelta(days=7)

            availabilities = DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor.id,
                DoctorAvailability.date >= today,
                DoctorAvailability.date <= next_week
            ).order_by(DoctorAvailability.date).all()

            return jsonify([avail.to_dict() for avail in availabilities]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif request.method == 'POST':
        data = request.get_json()

        required_fields = ['date', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        try:
            # Check if availability already exists
            availability_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            existing = DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor.id,
                DoctorAvailability.date == availability_date
            ).first()

            if existing:
                # Update existing
                existing.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
                existing.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
                existing.is_available = data.get('is_available', True)
            else:
                # Create new
                availability = DoctorAvailability(
                    doctor_id=doctor.id,
                    date=availability_date,
                    start_time=datetime.strptime(data['start_time'], '%H:%M').time(),
                    end_time=datetime.strptime(data['end_time'], '%H:%M').time(),
                    is_available=data.get('is_available', True)
                )
                db.session.add(availability)

            db.session.commit()

            cache_clear_pattern('doctors:*')

            return jsonify({'message': 'Availability updated successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
