@echo off
echo ========================================
echo Starting Hospital Management System Backend
echo ========================================
echo.

cd backend

echo Activating virtual environment...
call venv\Scripts\activate
echo.

echo Starting Flask server on http://localhost:5000
echo Press Ctrl+C to stop
echo.

python start_backend.py
