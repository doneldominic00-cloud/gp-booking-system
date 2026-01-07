from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import GPAvailability, Appointment, GP
from .utils import is_slot_available
from django.core.mail import send_mail
from django.urls import reverse

@login_required
def available_slots(request):
    slots = GPAvailability.objects.filter(is_blocked=False).order_by('date','start_time')
    return render(request, 'appointments/available_slots.html', {'slots': slots})

@login_required
def book_appointment(request, slot_id):
    slot = get_object_or_404(GPAvailability, id=slot_id, is_blocked=False)
    if not is_slot_available(slot.gp, slot.date, slot.start_time, slot.end_time):
        return render(request, 'appointments/error.html', {'message': 'Slot already booked.'})
    appt = Appointment.objects.create(
        patient=request.user,
        gp=slot.gp,
        date=slot.date,
        start_time=slot.start_time,
        end_time=slot.end_time
    )
    slot.is_blocked = True
    slot.save()

    send_mail(
        'Appointment Confirmation',
        f'Your appointment with {slot.gp} on {slot.date} at {slot.start_time} is confirmed.',
        None,
        [request.user.email],
        fail_silently=True
    )
    return redirect(reverse('appointments:book_success', args=[appt.id]))

@login_required
def book_success(request, appt_id):
    appt = get_object_or_404(Appointment, id=appt_id, patient=request.user)
    return render(request, 'appointments/book_success.html', {'appointment': appt})

@user_passes_test(lambda u: u.is_admin_staff())
def block_slot(request, slot_id):
    slot = get_object_or_404(GPAvailability, id=slot_id)
    slot.is_blocked = True
    slot.save()
    return redirect('appointments:available_slots')
def home(request):
    return render(request,"home.html")