@echo off
echo ========================================
echo Starting Celery Worker
echo ========================================
echo.

cd backend

echo Activating virtual environment...
call venv\Scripts\activate
echo.

echo Starting Celery worker...
echo Press Ctrl+C to stop
echo.

celery -A app.tasks.celery worker --pool=solo --loglevel=info
