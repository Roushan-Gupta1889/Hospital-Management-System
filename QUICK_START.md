# Hospital Management System - Quick Start Guide

## Prerequisites
- Python 3.8+
- Node.js 16+
- Redis Server

## Quick Setup (Windows)

### 1. Install Redis
Download and install Redis from: https://github.com/microsoftarchive/redis/releases

Start Redis:
```bash
redis-server
```

### 2. Setup Backend (Automated)
Double-click: `setup_backend.bat`

Or manually:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Frontend (Automated)
Double-click: `setup_frontend.bat`

Or manually:
```bash
cd frontend
npm install
```

## Running the Application

### Terminal 1: Redis Server
```bash
redis-server
```

### Terminal 2: Backend Server
Double-click: `run_backend.bat`

Or manually:
```bash
cd backend
venv\Scripts\activate
python start_backend.py
```

### Terminal 3: Celery Worker
Double-click: `run_celery.bat`

Or manually:
```bash
cd backend
venv\Scripts\activate
celery -A app.tasks.celery worker --pool=solo --loglevel=info
```

### Terminal 4: Frontend Server
Double-click: `run_frontend.bat`

Or manually:
```bash
cd frontend
npm run dev
```

## Access the Application

Open browser: http://localhost:3000

### Default Admin Credentials
- Username: `admin`
- Password: `admin123`

## Quick Test Flow

1. **Login as Admin** (admin/admin123)
2. **Add a Doctor**:
   - Navigate to "Doctors" → "Add Doctor"
   - Fill in doctor details
   - Save

3. **Register as Patient**:
   - Logout
   - Click "Register" tab
   - Fill in patient details
   - Register

4. **Book Appointment**:
   - Login as patient
   - Go to "Doctors"
   - Click "Book Appointment"
   - Select date, time, reason
   - Book

5. **Complete Appointment**:
   - Logout
   - Login as doctor
   - Go to "Appointments"
   - Click "Complete"
   - Add diagnosis and treatment
   - Save

6. **View Treatment History**:
   - Logout
   - Login as patient
   - Go to "Appointments"
   - View completed appointment details

## Project Structure
```
project_Hospital_001/
├── backend/           # Flask API
├── frontend/          # Vue.js UI
├── README.md          # Full documentation
├── GUIDELINE.txt      # Implementation guide
├── demo_instructions.txt  # Detailed demo steps
└── QUICK_START.md     # This file
```

## Common Issues

### Port Already in Use
- Backend (5000): Change port in `start_backend.py`
- Frontend (3000): Change port in `vite.config.js`

### Redis Connection Error
- Ensure Redis server is running
- Check Redis is on default port 6379

### Module Not Found
- Activate virtual environment
- Reinstall requirements: `pip install -r requirements.txt`

## Need More Help?
- See `README.md` for complete documentation
- Check `demo_instructions.txt` for detailed walkthrough
- Review `GUIDELINE.txt` for implementation details
