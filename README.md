# Hospital Management System V2

A comprehensive web-based Hospital Management System built with Flask (backend) and Vue.js (frontend) that enables efficient management of patients, doctors, appointments, and treatments.

## Features

### Role-Based Access Control
The system supports three user roles with distinct functionalities:

#### Admin (Hospital Staff)
- Pre-existing superuser with highest access level
- Dashboard displaying total doctors, patients, and appointments
- Add, update, and delete doctor profiles
- Manage patient information
- View and manage all appointments
- Search for patients or doctors by name/specialization
- Deactivate/blacklist doctors and patients

#### Doctor
- Login to view assigned appointments
- Dashboard showing upcoming appointments and patient list
- Mark appointments as completed with diagnosis and treatment notes
- Update patient treatment history (diagnosis, prescriptions)
- Provide availability for the next 7 days
- View patient medical history for informed consultation

#### Patient
- Self-registration and login
- View available departments and specializations
- Search doctors by specialization and availability
- Book, reschedule, or cancel appointments
- View appointment history with treatment details
- Export treatment history as CSV
- Edit profile information

### Core Functionalities

1. **Appointment Management**
   - Prevents double booking (conflict prevention)
   - Dynamic status updates (Booked → Completed → Cancelled)
   - Appointment history tracking
   - Treatment records with diagnosis and prescriptions

2. **Search & Filter**
   - Search doctors by name or specialization
   - Search patients by name, ID, or contact information
   - Filter appointments by status

3. **Backend Jobs (Celery + Redis)**
   - **Daily Reminders**: Automated daily reminders for scheduled appointments
   - **Monthly Reports**: Activity reports for doctors sent on first day of each month
   - **CSV Export**: User-triggered async job to export patient treatment history

4. **Performance Optimization**
   - Redis caching for frequently accessed data
   - Cache expiry management
   - Optimized API responses

## Technology Stack

### Backend
- **Flask**: Web framework for API
- **SQLAlchemy**: ORM for database management
- **SQLite**: Database (created programmatically)
- **Redis**: Caching and message broker
- **Celery**: Asynchronous task queue for background jobs
- **Flask-CORS**: Cross-origin resource sharing
- **Werkzeug**: Password hashing and security

### Frontend
- **Vue.js 3**: Progressive JavaScript framework
- **Vue Router**: Client-side routing
- **Axios**: HTTP client for API calls
- **Bootstrap 5**: UI components and styling
- **Vite**: Build tool and development server

## Project Structure

```
project_Hospital_001/
│
├── backend/
│   ├── start_backend.py        # Flask entry point
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py          # App initialization
│   │   ├── models.py            # Database models
│   │   ├── utils.py             # Utility functions
│   │   ├── tasks.py             # Celery tasks
│   │   └── routes/
│   │       ├── auth.py          # Authentication routes
│   │       ├── admin.py         # Admin routes
│   │       ├── doctor.py        # Doctor routes
│   │       ├── patient.py       # Patient routes
│   │       └── appointments.py  # Appointment routes
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── router.js
│       ├── App.vue
│       ├── views/
│       │   ├── Login.vue
│       │   ├── Dashboard.vue
│       │   ├── Patients.vue
│       │   ├── Doctors.vue
│       │   └── Appointments.vue
│       └── components/
│           └── Navbar.vue
│
├── README.md
└── demo_instructions.txt
```

## Database Schema

### Models

1. **User**: Base user model with authentication
   - Fields: id, username, email, password_hash, role, full_name, phone, is_active

2. **Department**: Medical departments/specializations
   - Fields: id, name, description

3. **Doctor**: Doctor profile extending User
   - Fields: id, user_id, department_id, specialization, qualification, experience_years, consultation_fee

4. **DoctorAvailability**: Doctor's available time slots
   - Fields: id, doctor_id, date, start_time, end_time, is_available

5. **Patient**: Patient profile extending User
   - Fields: id, user_id, date_of_birth, gender, address, blood_group, emergency_contact, medical_history

6. **Appointment**: Appointment bookings
   - Fields: id, patient_id, doctor_id, appointment_date, appointment_time, status, reason, notes

7. **Treatment**: Treatment records for completed appointments
   - Fields: id, appointment_id, diagnosis, prescription, treatment_notes, next_visit_date

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Redis Server

### Backend Setup

1. Navigate to backend directory:
```bash
cd project_Hospital_001/backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start Redis server:
```bash
redis-server
```

5. Start Celery worker (in a new terminal):
```bash
cd backend
celery -A app.tasks.celery worker --loglevel=info
```

6. Start Celery beat scheduler (in another terminal):
```bash
cd backend
celery -A app.tasks.celery beat --loglevel=info
```

7. Run Flask application:
```bash
python start_backend.py
```

The backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd project_Hospital_001/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Default Credentials

### Admin
- **Username**: admin
- **Password**: admin123

Note: Admin is automatically created when the application first runs.

### Creating Additional Users
- **Doctors**: Created by Admin through the admin panel
- **Patients**: Self-registration available on the login page

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new patient
- `POST /api/auth/login` - Login (all roles)
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user info

### Admin Routes
- `GET /api/admin/dashboard` - Get dashboard statistics
- `GET /api/admin/departments` - List all departments
- `POST /api/admin/departments` - Create department
- `GET /api/admin/doctors` - List all doctors
- `POST /api/admin/doctors` - Create doctor
- `PUT /api/admin/doctors/:id` - Update doctor
- `DELETE /api/admin/doctors/:id` - Deactivate doctor
- `GET /api/admin/patients` - List all patients
- `PUT /api/admin/patients/:id` - Update patient
- `DELETE /api/admin/patients/:id` - Deactivate patient
- `GET /api/admin/appointments` - View all appointments

### Doctor Routes
- `GET /api/doctor/dashboard` - Doctor dashboard
- `GET /api/doctor/appointments` - Get doctor's appointments
- `POST /api/doctor/appointments/:id/complete` - Complete appointment
- `POST /api/doctor/appointments/:id/cancel` - Cancel appointment
- `GET /api/doctor/patients/:id/history` - Get patient history
- `GET /api/doctor/availability` - Get availability
- `POST /api/doctor/availability` - Set availability

### Patient Routes
- `GET /api/patient/dashboard` - Patient dashboard
- `GET /api/patient/profile` - Get patient profile
- `PUT /api/patient/profile` - Update profile
- `GET /api/patient/doctors` - Search doctors
- `GET /api/patient/appointments` - Get appointments
- `GET /api/patient/appointments/history` - Get appointment history
- `POST /api/patient/export-treatments` - Export treatment history

### Appointment Routes
- `POST /api/appointments` - Book appointment
- `GET /api/appointments/:id` - Get appointment details
- `PUT /api/appointments/:id` - Reschedule appointment
- `DELETE /api/appointments/:id` - Cancel appointment
- `POST /api/appointments/check-availability` - Check time slot availability

## Features Implemented by Milestone

### Milestone 1: Database Models and Schema Setup ✅
- All database models created programmatically
- Relationships established between entities
- SQLite database with proper constraints

### Milestone 2: Authentication and Role-Based Access ✅
- Session-based authentication
- Role-based access control (Admin, Doctor, Patient)
- Password hashing with Werkzeug
- Login/logout functionality

### Milestone 3: Admin Dashboard and Management ✅
- Dashboard with statistics
- CRUD operations for doctors and patients
- Department management
- Search functionality
- User deactivation

### Milestone 4: Doctor Dashboard & Management ✅
- Doctor dashboard with upcoming appointments
- Complete appointments with treatment details
- Patient history viewing
- Availability management

### Milestone 5: Patient Dashboard and Appointment System ✅
- Patient registration and login
- View departments and doctors
- Book, reschedule, cancel appointments
- View appointment history
- Profile management

### Milestone 6: Appointment History and Conflict Prevention ✅
- Appointment history with treatment details
- Conflict prevention for double booking
- Dynamic status updates
- Treatment record storage

### Milestone 7: Backend Jobs ✅
- Daily reminders using Celery Beat
- Monthly activity reports for doctors
- Async CSV export for patient treatments

### Milestone 8: API Performance & Caching ✅
- Redis caching for frequently accessed data
- Cache expiry management
- Optimized database queries

## Caching Strategy

The application uses Redis for caching with the following keys:
- `admin:dashboard` - Admin dashboard statistics (5 min expiry)
- `patient:{id}:dashboard` - Patient dashboard data (2 min expiry)
- `patient:{id}:history` - Patient treatment history (5 min expiry)
- `doctors:search:*` - Doctor search results (3 min expiry)
- `departments:*` - Department lists

Cache is automatically invalidated on relevant data changes.

## Background Jobs

### Daily Reminders
- Runs every day
- Sends reminders to patients with appointments scheduled for that day
- Can be configured to send via email/SMS/Google Chat

### Monthly Reports
- Runs on the first day of each month
- Generates HTML report with doctor's monthly activity
- Includes appointment statistics and treatment details

### CSV Export
- User-triggered asynchronous job
- Exports patient treatment history
- Saves to exports/ directory
- Returns task ID for status tracking

## Development Notes

- The database is created automatically on first run
- Admin user is created programmatically
- All API responses use JSON format
- Bootstrap 5 is used for responsive design
- Vue Router handles client-side navigation
- Axios interceptors can be added for authentication headers

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Role-based access control on all routes
- SQL injection prevention via SQLAlchemy ORM
- CORS configuration for secure cross-origin requests

## Future Enhancements

- Email/SMS integration for reminders
- Payment gateway integration
- Prescription PDF generation
- Medical report uploads
- Video consultation feature
- Advanced analytics and reporting

## License

This project is developed as part of an academic assignment.

## Contact

For issues or questions, please refer to the demo_instructions.txt file.
