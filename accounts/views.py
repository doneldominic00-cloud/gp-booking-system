from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth import get_user_model

from appointments.models import Appointment

User = get_user_model()


def signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        username = request.POST.get('username')
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
                username=username,
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
def my_appointments(request):
    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by('-appointment_date')

    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments
    })


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    appointment.status = 'cancelled'
    appointment.save()
    messages.success(request, 'Appointment cancelled successfully.')
    return redirect('accounts:my_appointments')


@login_required
def book_appointment_redirect(request):
    return redirect('appointments:available_slots')
