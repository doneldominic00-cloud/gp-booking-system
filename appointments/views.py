from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta

from .models import GPAvailability, Appointment
from .utils import is_slot_available


def home(request):
    """Homepage view"""
    return render(request, 'home.html')


@login_required
def calendar_view(request):
    """Display the calendar interface for booking appointments"""
    return render(request, 'appointments/calendar.html')


@login_required
def slots_feed(request):
    """JSON feed of available appointment slots for FullCalendar"""
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    
    if start_str and end_str:
        start_date = parse_date(start_str.split('T')[0])
        end_date = parse_date(end_str.split('T')[0])
    else:
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
    
    available_slots = GPAvailability.objects.filter(
        is_blocked=False,
        date__gte=start_date,
        date__lte=end_date
    ).select_related('gp')
    
    events = []
    for slot in available_slots:
        slot_datetime = timezone.make_aware(
            datetime.combine(slot.date, slot.start_time)
        )
        end_datetime = timezone.make_aware(
            datetime.combine(slot.date, slot.end_time)
        )
        
        doctor_name = str(slot.gp).replace('Dr. ', '')
        
        if slot_datetime > timezone.now():
            events.append({
                'id': str(slot.id),
                'title': f"Dr. {doctor_name}",
                'start': slot_datetime.isoformat(),
                'end': end_datetime.isoformat(),
                'backgroundColor': '#28a745',
                'borderColor': '#28a745',
                'extendedProps': {
                    'gp_id': slot.gp.id,
                    'gp_name': doctor_name
                }
            })
    
    return JsonResponse(events, safe=False)


@require_POST
@csrf_protect
@login_required
def book_slot_api(request, slot_id):
    """Books a slot via AJAX. Returns JSON success/error"""
    try:
        slot = get_object_or_404(GPAvailability, id=slot_id, is_blocked=False)
    except:
        return JsonResponse({'ok': False, 'error': 'Slot not found or already booked.'}, status=404)

    if not is_slot_available(slot.gp, slot.date, slot.start_time, slot.end_time):
        return JsonResponse({'ok': False, 'error': 'Slot already booked.'}, status=409)

    appointment_datetime = timezone.make_aware(
        datetime.combine(slot.date, slot.start_time)
    )

    appt = Appointment.objects.create(
        patient=request.user,
        doctor=slot.gp.user,
        appointment_date=appointment_datetime,
        status='confirmed'
    )

    slot.is_blocked = True
    slot.save()

    if request.user.email:
        doctor_name = str(slot.gp)
        send_mail(
            'Appointment Confirmation',
            f'Your appointment with Dr. {doctor_name} on {slot.date} at {slot.start_time} is confirmed.',
            None,
            [request.user.email],
            fail_silently=True,
        )

    return JsonResponse({'ok': True, 'appointment_id': appt.id})
