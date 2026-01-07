# GP Booking System - Django

This repository is a starter scaffold for the **GP Appointment Booking System** (Django).
It implements patient and admin user types, GP availability, booking, conflict prevention,
email confirmations (console backend by default), and a small admin setup.

## Quick start (local)

1. Create a Python virtualenv and activate it:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run migrations and create a superuser:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. Open http://127.0.0.1:8000/

## Docker (development)
```bash
docker-compose up --build
```

## Notes
- Default email backend prints to console. Configure SMTP in production.
- Uses SQLite by default; set DATABASE_URL to use PostgreSQL.
- Project is based on the user's project document (Booking System for GP Appointments). See the dissertation.pdf for full requirements.
