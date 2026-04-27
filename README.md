
GP Appointment Booking System
Student: Donel Dominic
Student ID: 40367822
Module: CSC3032 Software Engineering Project
University: Queen's University Belfast

Project Overview
A web-based GP appointment booking system built with Python and Django. The system allows patients to register, browse GP availability on an interactive calendar, book and cancel appointments, and receive automated email confirmations and reminders. Admin staff can manage GP availability through a dedicated management portal. The system also includes an AI-powered health chat assistant powered by the Groq API.

Features

Patient registration and secure login
Interactive calendar booking interface using FullCalendar
Appointment booking, viewing and cancellation
Automated email confirmation on booking
24-hour email reminder system via Django management command
Admin portal for managing GP availability slots
AI health chat assistant for general health queries
Role-based access control (Patient and Admin Staff)


Tech Stack
LayerTechnologyBackendPython 3.15, Django 5.2DatabaseSQLite (development) / PostgreSQL (production)FrontendDjango Templates, Bootstrap 5, Vanilla JavaScriptCalendarFullCalendarAI ChatGroq API (Llama 3.3)EmailDjango Email Backend (SMTP)Version ControlGit, GitHub, GitLab

Project Structure
gp_booking_system/
├── accounts/                  # User management app
│   ├── models.py              # Custom User model
│   ├── views.py               # Registration, login, profile views
│   ├── urls.py                # Account URL routes
│   └── templates/accounts/    # Account templates
├── appointments/              # Booking management app
│   ├── models.py              # GP, GPAvailability, Appointment models
│   ├── views.py               # Booking, calendar, AI chat views
│   ├── urls.py                # Appointment URL routes
│   ├── utils.py               # is_slot_available() utility function
│   ├── tests.py               # Automated unit tests
│   └── management/commands/   # send_reminders management command
├── templates/                 # Base and shared templates
├── gp_booking_system/         # Project settings and URL config
├── requirements.txt           # Project dependencies
├── .env                       # Environment variables (not tracked in git)
└── manage.py                  # Django management script

Installation and Setup
Prerequisites

Python 3.10 or higher
pip

Steps
1. Clone the repository
bashgit clone <https://gitlab.eeecs.qub.ac.uk/40367822/gp-booking-system.git>
cd gp_booking_system
2. Install dependencies
bashpip install -r requirements.txt
3. Create a .env file in the project root
GROQ_API_KEY=your-groq-api-key-here
SECRET_KEY=your-django-secret-key-here
DEBUG=1
4. Apply migrations
bashpython manage.py migrate
5. Create a superuser (admin account)
bashpython manage.py createsuperuser
6. Run the development server
bashpython manage.py runserver
7. Visit the application
http://127.0.0.1:8000

Running Tests
bashpython manage.py test appointments -v 2
All 5 tests should pass successfully.

Running Email Reminders
To manually trigger the 24-hour appointment reminder emails:
bashpython manage.py send_reminders

User Roles
RoleAccessPatientRegister, login, view calendar, book and cancel appointments, use AI chatAdmin StaffAll patient access plus manage GP availability, view all appointments

Known Limitations

System runs on localhost only and has not been deployed publicly due to GDPR considerations
Mobile testing was not formally carried out
Automated test coverage is limited to core booking functionality
Session timeout for inactive users has not been implemented