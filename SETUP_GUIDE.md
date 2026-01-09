# Hospital Management System - Complete Setup Guide

## Overview
A professional, full-featured Hospital Management System with role-based access control for Admins, Doctors, and Patients.

## Features
- **Admin Dashboard**: Manage doctors, patients, and appointments
- **Doctor Dashboard**: View appointments, add diagnosis and treatment
- **Patient Dashboard**: Book appointments, view treatment history
- **Real-time Updates**: With Redis caching and Celery background tasks
- **Professional UI**: Modern, responsive design with smooth animations

---

## Prerequisites

Before starting, ensure you have the following installed:

### Required Software:
1. **Python 3.8+** - [Download](https://www.python.org/downloads/)
2. **Node.js 16+** - [Download](https://nodejs.org/)
3. **Redis Server** - [Download for Windows](https://github.com/microsoftarchive/redis/releases)

### Verify Installation:
```bash
python --version
node --version
npm --version
```

---

## Step-by-Step Setup

### 1. Install and Start Redis

#### Windows:
1. Download Redis from: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`
3. Keep this terminal window open

#### Mac/Linux:
```bash
# Install Redis
brew install redis  # Mac
sudo apt-get install redis-server  # Ubuntu

# Start Redis
redis-server
```

You should see: `Ready to accept connections on port 6379`

---

### 2. Backend Setup

#### Option A: Automated Setup (Recommended)
```bash
# Double-click the batch file:
setup_backend.bat
```

#### Option B: Manual Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### 3. Frontend Setup

#### Option A: Automated Setup (Recommended)
```bash
# Double-click the batch file:
setup_frontend.bat
```

#### Option B: Manual Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

---

### 4. Initialize Sample Data (Important!)

After setting up the backend, initialize sample data:

```bash
cd backend
venv\Scripts\activate
python init_sample_data.py
```

This creates:
- ✅ 5 Departments (Cardiology, Neurology, etc.)
- ✅ 3 Sample Doctors
- ✅ 2 Sample Patients

---

## Running the Application

You need **4 separate terminal windows** running simultaneously:

### Terminal 1: Redis Server
```bash
redis-server
```
**Status**: ✅ Ready to accept connections

---

### Terminal 2: Backend Server
```bash
cd backend
venv\Scripts\activate
python start_backend.py
```
**Status**: ✅ Running on http://localhost:5000

---

### Terminal 3: Celery Worker (Background Tasks)
```bash
cd backend
venv\Scripts\activate
celery -A app.tasks.celery worker --pool=solo --loglevel=info
```
**Status**: ✅ Celery worker ready

---

### Terminal 4: Frontend Development Server
```bash
cd frontend
npm run dev
```
**Status**: ✅ Running on http://localhost:3000

---

## Access the Application

🌐 **Open your browser**: http://localhost:3000

---

## Login Credentials

### Admin Account
```
Username: admin
Password: admin123
```

### Sample Doctor Accounts
```
Username: drjohn    | Password: doctor123
Username: drsarah   | Password: doctor123
Username: drmike    | Password: doctor123
```

### Sample Patient Accounts
```
Username: johndoe   | Password: patient123
Username: janedoe   | Password: patient123
```

---

## User Roles & Features

### 👨‍💼 Admin Features:
- ✅ View dashboard with statistics
- ✅ Manage doctors (Add, Edit, Deactivate)
- ✅ Manage patients (View, Deactivate)
- ✅ View all appointments
- ✅ Search functionality

### 👨‍⚕️ Doctor Features:
- ✅ View personal dashboard
- ✅ View assigned appointments
- ✅ Complete appointments with diagnosis
- ✅ Add treatment and prescriptions
- ✅ View patient medical history

### 🧑‍🦱 Patient Features:
- ✅ Self-registration
- ✅ Search doctors by specialization
- ✅ Book appointments
- ✅ View appointment history
- ✅ View treatment details
- ✅ Export treatment history

---

## Project Architecture

```
project_Hospital_001/
├── backend/                    # Flask API Backend
│   ├── app/
│   │   ├── __init__.py        # App initialization
│   │   ├── models.py          # Database models
│   │   ├── tasks.py           # Celery background tasks
│   │   ├── utils.py           # Utility functions
│   │   └── routes/            # API endpoints
│   │       ├── auth.py        # Authentication
│   │       ├── admin.py       # Admin routes
│   │       ├── doctor.py      # Doctor routes
│   │       ├── patient.py     # Patient routes
│   │       └── appointments.py
│   ├── start_backend.py       # Backend entry point
│   └── init_sample_data.py    # Sample data script
│
├── frontend/                   # Vue.js Frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   │   └── Navbar.vue
│   │   ├── views/             # Page components
│   │   │   ├── Login.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── Doctors.vue
│   │   │   ├── Patients.vue
│   │   │   └── Appointments.vue
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── router.js
│   └── package.json
│
└── SETUP_GUIDE.md             # This file
```

---

## Tech Stack

### Backend:
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database
- **SQLite** - Database
- **Redis** - Caching & message broker
- **Celery** - Background task processing
- **Flask-CORS** - Cross-origin support

### Frontend:
- **Vue.js 3** - Progressive JavaScript framework
- **Vue Router** - Client-side routing
- **Axios** - HTTP client
- **Bootstrap 5** - UI framework
- **Bootstrap Icons** - Icon library
- **Vite** - Build tool

---

## Troubleshooting

### Issue: "Port already in use"

**Backend Port 5000:**
```python
# Edit backend/start_backend.py
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001
```

**Frontend Port 3000:**
```javascript
// Edit frontend/vite.config.js
server: {
  port: 3001  // Change to 3001
}
```

---

### Issue: "Redis connection error"

**Solution:**
1. Make sure Redis server is running
2. Check it's on port 6379: `redis-cli ping` (should return PONG)
3. Restart Redis server

---

### Issue: "Module not found" (Backend)

**Solution:**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt --force-reinstall
```

---

### Issue: "Cannot find module" (Frontend)

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

### Issue: "Database is locked"

**Solution:**
```bash
cd backend
# Delete the database and recreate
rm hospital.db
python start_backend.py  # Will auto-create DB
python init_sample_data.py  # Repopulate data
```

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new patient
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Admin
- `GET /api/admin/dashboard` - Dashboard stats
- `GET /api/admin/doctors` - List doctors
- `POST /api/admin/doctors` - Create doctor
- `GET /api/admin/patients` - List patients
- `GET /api/admin/appointments` - View all appointments

### Doctor
- `GET /api/doctor/dashboard` - Doctor dashboard
- `GET /api/doctor/appointments` - Get appointments
- `POST /api/doctor/appointments/:id/complete` - Complete appointment

### Patient
- `GET /api/patient/dashboard` - Patient dashboard
- `GET /api/patient/doctors` - Search doctors
- `POST /api/appointments` - Book appointment
- `GET /api/patient/appointments` - Get appointments

---

## Testing Workflow

1. **Login as Admin** (admin / admin123)
   - View dashboard statistics
   - Browse doctors and patients

2. **Add a New Doctor** (Admin)
   - Navigate to "Doctors" → Click "Add Doctor"
   - Fill in details and save

3. **Register as Patient**
   - Logout → Click "Register" tab
   - Fill patient details and register

4. **Book Appointment** (Patient)
   - Login with patient credentials
   - Go to "Find Doctors"
   - Click "Book Appointment" on any doctor

5. **Complete Appointment** (Doctor)
   - Login with doctor credentials
   - Go to "My Appointments"
   - Click "Complete" and add diagnosis

6. **View Treatment History** (Patient)
   - Login as patient
   - View completed appointments with treatment details

---

## Production Deployment Notes

### Security Improvements:
1. Change `SECRET_KEY` in `backend/app/__init__.py`
2. Use PostgreSQL instead of SQLite
3. Enable HTTPS
4. Use environment variables for sensitive data
5. Set `debug=False` in production

### Environment Variables:
```bash
export SECRET_KEY="your-secret-key"
export DATABASE_URL="postgresql://user:password@host/dbname"
export REDIS_URL="redis://localhost:6379/0"
```

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `README.md` and `QUICK_START.md`
3. Check `demo_instructions.txt` for detailed workflows

---

## License

Academic project - for educational purposes only.

---

**🎉 Congratulations! Your Hospital Management System is now ready to use!**
