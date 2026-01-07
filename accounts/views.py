from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from datetime import datetime, timedelta, time
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# Import Appointment model
try:
    from appointments.models import Appointment
    # Check what fields the model actually has
    appointment_fields = [f.name for f in Appointment._meta.get_fields()]
except ImportError:
    Appointment = None
    appointment_fields = []

def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type', 'patient')
        
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'accounts/signup.html')
        
        try:
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:profile')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
    
    return render(request, 'accounts/signup.html')

@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def book_appointment(request):
    if not Appointment:
        messages.error(request, 'Appointment system not configured yet.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason', '')
        
        try:
            # Get doctor user
            doctor = User.objects.get(id=doctor_id, user_type='doctor')
            appointment_datetime = datetime.strptime(
                f"{appointment_date} {appointment_time}", 
                "%Y-%m-%d %H:%M"
            )
            
            # Make timezone aware
            if timezone.is_naive(appointment_datetime):
                appointment_datetime = timezone.make_aware(appointment_datetime)
            
            # Check if slot is available
            existing = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_datetime
            ).exists()
            
            if existing:
                messages.error(request, 'This time slot is already booked.')
            else:
                # Create appointment with only the fields that exist
                appointment_data = {
                    'patient': request.user,
                    'doctor': doctor,
                    'appointment_date': appointment_datetime,
                }
                
                # Add optional fields if they exist in the model
                if 'reason' in appointment_fields:
                    appointment_data['reason'] = reason
                if 'status' in appointment_fields:
                    appointment_data['status'] = 'scheduled'
                
                Appointment.objects.create(**appointment_data)
                messages.success(request, 'Appointment booked successfully!')
                return redirect('accounts:my_appointments')
        except User.DoesNotExist:
            messages.error(request, 'Selected doctor not found.')
        except Exception as e:
            messages.error(request, f'Error booking appointment: {str(e)}')
    
    # Get available doctors
    doctors = User.objects.filter(user_type='doctor', is_active=True)
    
    # Generate next 14 days for calendar as date objects
    today = timezone.now().date()
    available_dates = [today + timedelta(days=i) for i in range(1, 15)]
    
    # Generate time slots (9 AM to 5 PM, 30-min intervals)
    time_slots = []
    start_time = time(9, 0)
    end_time = time(17, 0)
    current = datetime.combine(today, start_time)
    end = datetime.combine(today, end_time)
    
    while current < end:
        time_slots.append(current.strftime('%H:%M'))
        current += timedelta(minutes=30)
    
    context = {
        'doctors': doctors,
        'available_dates': available_dates,
        'time_slots': time_slots,
    }
    return render(request, 'appointments/book_appointment.html', context)

@login_required
def my_appointments(request):
    if not Appointment:
        messages.error(request, 'Appointment system not configured yet.')
        return redirect('accounts:profile')
    
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('-appointment_date')
    
    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments
    })

@login_required
def cancel_appointment(request, appointment_id):
    if not Appointment:
        messages.error(request, 'Appointment system not configured yet.')
        return redirect('accounts:profile')
    
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    # Check if model has status field
    if 'status' in appointment_fields:
        appointment.status = 'cancelled'
        appointment.save()
    else:
        # If no status field, just delete the appointment
        appointment.delete()
    
    messages.success(request, 'Appointment cancelled successfully.')
    return redirect('accounts:my_appointments')

from django.shortcuts import redirect

@login_required
def book_appointment_redirect(request):
    # Redirect to the calendar view for booking appointments
    return redirect('appointments:available_slots')
