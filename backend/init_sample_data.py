"""
Sample Data Initialization Script
Run this after first starting the backend to populate with sample data for demos
"""

from app import create_app, db
from app.models import User, Department, Doctor, Patient, Appointment
from datetime import datetime, date, timedelta, time

def init_sample_data():
    app = create_app()
    with app.app_context():
        print("Initializing sample data...")

        # Create Departments
        departments_data = [
            {"name": "Cardiology", "description": "Heart and cardiovascular system specialists"},
            {"name": "Neurology", "description": "Brain and nervous system specialists"},
            {"name": "Orthopedics", "description": "Bone and joint specialists"},
            {"name": "Pediatrics", "description": "Children's health specialists"},
            {"name": "General Medicine", "description": "General health and wellness"}
        ]

        departments = []
        for dept_data in departments_data:
            dept = Department.query.filter_by(name=dept_data['name']).first()
            if not dept:
                dept = Department(**dept_data)
                db.session.add(dept)
                departments.append(dept)
                print(f"Created department: {dept_data['name']}")
            else:
                departments.append(dept)

        db.session.commit()

        # Create Sample Doctors
        doctors_data = [
            {
                "username": "drjohn",
                "email": "john@hospital.com",
                "password": "doctor123",
                "full_name": "Dr. John Smith",
                "phone": "1234567890",
                "specialization": "Cardiologist",
                "qualification": "MD, Cardiology",
                "experience_years": 10,
                "consultation_fee": 100.0,
                "department_id": 1
            },
            {
                "username": "drsarah",
                "email": "sarah@hospital.com",
                "password": "doctor123",
                "full_name": "Dr. Sarah Johnson",
                "phone": "1234567891",
                "specialization": "Neurologist",
                "qualification": "MD, Neurology",
                "experience_years": 8,
                "consultation_fee": 120.0,
                "department_id": 2
            },
            {
                "username": "drmike",
                "email": "mike@hospital.com",
                "password": "doctor123",
                "full_name": "Dr. Mike Wilson",
                "phone": "1234567892",
                "specialization": "General Physician",
                "qualification": "MBBS, MD",
                "experience_years": 5,
                "consultation_fee": 50.0,
                "department_id": 5
            }
        ]

        for doctor_data in doctors_data:
            user = User.query.filter_by(username=doctor_data['username']).first()
            if not user:
                user = User(
                    username=doctor_data['username'],
                    email=doctor_data['email'],
                    role='doctor',
                    full_name=doctor_data['full_name'],
                    phone=doctor_data['phone']
                )
                user.set_password(doctor_data['password'])
                db.session.add(user)
                db.session.flush()

                doctor = Doctor(
                    user_id=user.id,
                    department_id=doctor_data['department_id'],
                    specialization=doctor_data['specialization'],
                    qualification=doctor_data['qualification'],
                    experience_years=doctor_data['experience_years'],
                    consultation_fee=doctor_data['consultation_fee']
                )
                db.session.add(doctor)
                print(f"Created doctor: {doctor_data['full_name']}")

        db.session.commit()

        # Create Sample Patients
        patients_data = [
            {
                "username": "johndoe",
                "email": "john.doe@email.com",
                "password": "patient123",
                "full_name": "John Doe",
                "phone": "9876543210",
                "gender": "Male",
                "blood_group": "O+",
                "address": "123 Main St, City"
            },
            {
                "username": "janedoe",
                "email": "jane.doe@email.com",
                "password": "patient123",
                "full_name": "Jane Doe",
                "phone": "9876543211",
                "gender": "Female",
                "blood_group": "A+",
                "address": "456 Oak Ave, City"
            }
        ]

        for patient_data in patients_data:
            user = User.query.filter_by(username=patient_data['username']).first()
            if not user:
                user = User(
                    username=patient_data['username'],
                    email=patient_data['email'],
                    role='patient',
                    full_name=patient_data['full_name'],
                    phone=patient_data['phone']
                )
                user.set_password(patient_data['password'])
                db.session.add(user)
                db.session.flush()

                patient = Patient(
                    user_id=user.id,
                    gender=patient_data['gender'],
                    blood_group=patient_data['blood_group'],
                    address=patient_data['address']
                )
                db.session.add(patient)
                print(f"Created patient: {patient_data['full_name']}")

        db.session.commit()

        print("\n" + "="*50)
        print("Sample data initialized successfully!")
        print("="*50)
        print("\nSample Credentials:")
        print("\nAdmin:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nDoctors:")
        print("  Username: drjohn   | Password: doctor123")
        print("  Username: drsarah  | Password: doctor123")
        print("  Username: drmike   | Password: doctor123")
        print("\nPatients:")
        print("  Username: johndoe  | Password: patient123")
        print("  Username: janedoe  | Password: patient123")
        print("="*50)

if __name__ == '__main__':
    init_sample_data()
