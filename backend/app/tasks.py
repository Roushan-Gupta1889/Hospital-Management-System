from celery import Celery
from datetime import datetime, timedelta, date
import csv
import io

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery.task
def send_daily_reminders():
    """Send daily reminders to patients with appointments today"""
    from app import create_app, db
    from app.models import Appointment

    app = create_app()
    with app.app_context():
        today = date.today()
        appointments = Appointment.query.filter(
            Appointment.appointment_date == today,
            Appointment.status == 'booked'
        ).all()

        for appointment in appointments:
            patient_name = appointment.patient.user.full_name
            doctor_name = appointment.doctor.user.full_name
            time = appointment.appointment_time.strftime('%H:%M')

            # In production, send via email/SMS/Google Chat
            message = f"Reminder: {patient_name} has an appointment with Dr. {doctor_name} today at {time}"
            print(f"REMINDER: {message}")

        return f"Sent {len(appointments)} reminders"

@celery.task
def send_monthly_report(doctor_id):
    """Generate and send monthly activity report for a doctor"""
    from app import create_app, db
    from app.models import Doctor, Appointment, Treatment

    app = create_app()
    with app.app_context():
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return "Doctor not found"

        # Get last month's data
        today = date.today()
        first_day = today.replace(day=1)
        last_month_end = first_day - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date >= last_month_start,
            Appointment.appointment_date <= last_month_end,
            Appointment.status == 'completed'
        ).all()

        # Generate HTML report
        html_content = f"""
        <html>
        <head><title>Monthly Activity Report - {doctor.user.full_name}</title></head>
        <body>
            <h1>Monthly Activity Report</h1>
            <h2>Dr. {doctor.user.full_name} - {doctor.specialization}</h2>
            <p>Period: {last_month_start.strftime('%B %Y')}</p>
            <p>Total Appointments: {len(appointments)}</p>

            <table border="1">
                <tr>
                    <th>Date</th>
                    <th>Patient</th>
                    <th>Diagnosis</th>
                    <th>Treatment</th>
                </tr>
        """

        for appointment in appointments:
            if appointment.treatment:
                html_content += f"""
                <tr>
                    <td>{appointment.appointment_date}</td>
                    <td>{appointment.patient.user.full_name}</td>
                    <td>{appointment.treatment.diagnosis}</td>
                    <td>{appointment.treatment.prescription}</td>
                </tr>
                """

        html_content += """
            </table>
        </body>
        </html>
        """

        # In production, send via email
        print(f"MONTHLY REPORT for Dr. {doctor.user.full_name}")
        print(html_content)

        return f"Report generated for {doctor.user.full_name}"

@celery.task
def export_patient_treatments_csv(patient_id):
    """Export patient treatment history as CSV"""
    from app import create_app, db
    from app.models import Patient, Appointment, Treatment

    app = create_app()
    with app.app_context():
        patient = Patient.query.get(patient_id)
        if not patient:
            return {"error": "Patient not found"}

        appointments = Appointment.query.filter(
            Appointment.patient_id == patient_id,
            Appointment.status == 'completed'
        ).all()

        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            'Patient ID',
            'Patient Name',
            'Doctor Name',
            'Appointment Date',
            'Diagnosis',
            'Treatment',
            'Next Visit'
        ])

        # Data rows
        for appointment in appointments:
            if appointment.treatment:
                writer.writerow([
                    patient.id,
                    patient.user.full_name,
                    appointment.doctor.user.full_name,
                    appointment.appointment_date,
                    appointment.treatment.diagnosis,
                    appointment.treatment.prescription,
                    appointment.treatment.next_visit_date or 'N/A'
                ])

        csv_content = output.getvalue()
        output.close()

        # In production, save to file system or send via email
        filename = f"patient_{patient_id}_treatments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = f"exports/{filename}"

        # For now, store in a temporary location
        import os
        os.makedirs('exports', exist_ok=True)
        with open(filepath, 'w', newline='') as f:
            f.write(csv_content)

        return {
            "filename": filename,
            "filepath": filepath,
            "status": "completed"
        }

# Configure Celery beat schedule
celery.conf.beat_schedule = {
    'send-daily-reminders': {
        'task': 'app.tasks.send_daily_reminders',
        'schedule': timedelta(days=1),  # Run every day
    },
    'send-monthly-reports': {
        'task': 'app.tasks.send_monthly_report',
        'schedule': timedelta(days=30),  # Run monthly
    },
}
