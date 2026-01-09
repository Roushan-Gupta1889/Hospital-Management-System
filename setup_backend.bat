@echo off
echo ========================================
echo Hospital Management System - Backend Setup
echo ========================================
echo.

cd backend

echo Creating virtual environment...
python -m venv venv
echo.

echo Activating virtual environment...
call venv\Scripts\activate
echo.

echo Installing dependencies...
pip install -r requirements.txt
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the backend server:
echo 1. cd backend
echo 2. venv\Scripts\activate
echo 3. python start_backend.py
echo.
pause
