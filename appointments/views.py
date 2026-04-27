import json
import groq as groq_lib

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import datetime, timedelta

from .models import GP, GPAvailability, Appointment
from .utils import is_slot_available


def is_admin(user):
    return user.is_authenticated and (user.is_admin_staff() or user.is_superuser)


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

    try:
        body = json.loads(request.body)
        reason = body.get('reason', '').strip()
    except (json.JSONDecodeError, AttributeError):
        reason = ''

    appt = Appointment.objects.create(
        patient=request.user,
        doctor=slot.gp.user,
        appointment_date=appointment_datetime,
        reason=reason,
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


@user_passes_test(is_admin)
def manage_availability(request):
    """Admin portal: lists all GPs and their availability slots."""
    gps = GP.objects.select_related('user').all()
    slots = GPAvailability.objects.select_related('gp__user').order_by('date', 'start_time')
    return render(request, 'appointments/manage_availability.html', {
        'gps': gps,
        'slots': slots,
    })


@require_POST
@user_passes_test(is_admin)
def add_availability(request):
    """Admin portal: create a new GPAvailability slot."""
    gp_id = request.POST.get('gp_id')
    date = request.POST.get('date')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')

    if not all([gp_id, date, start_time, end_time]):
        messages.error(request, 'All fields are required.')
        return redirect('appointments:manage_availability')

    gp = get_object_or_404(GP, id=gp_id)
    _, created = GPAvailability.objects.get_or_create(
        gp=gp,
        date=date,
        start_time=start_time,
        end_time=end_time,
    )

    if created:
        messages.success(request, f'Slot added for {gp} on {date}.')
    else:
        messages.warning(request, 'That slot already exists.')

    return redirect('appointments:manage_availability')


@require_POST
@user_passes_test(is_admin)
def block_slot(request, slot_id):
    """Admin portal: mark a slot as blocked."""
    slot = get_object_or_404(GPAvailability, id=slot_id)
    slot.is_blocked = True
    slot.save()
    messages.success(request, f'Slot on {slot.date} at {slot.start_time} has been blocked.')
    return redirect('appointments:manage_availability')


@require_POST
@login_required
def ai_chat_api(request):
    """Respond to a patient's health question using the Groq API."""
    try:
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid request body.'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Message cannot be empty.'}, status=400)

    api_key = settings.GROQ_API_KEY
    if not api_key:
        return JsonResponse({'error': 'AI assistant is not configured.'}, status=503)

    try:
        client = groq_lib.Groq(api_key=api_key)
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            max_tokens=512,
            messages=[
                {
                    'role': 'system',
                    'content': (
                        'You are a helpful medical assistant for a GP booking system. '
                        'You can answer general health questions clearly and compassionately. '
                        'Always recommend that patients see a doctor for serious, urgent, or '
                        'persistent concerns. Never diagnose conditions or prescribe treatments.'
                    ),
                },
                {'role': 'user', 'content': user_message},
            ],
        )
        reply = response.choices[0].message.content
        return JsonResponse({'reply': reply})
    except groq_lib.AuthenticationError:
        return JsonResponse({'error': 'AI assistant authentication failed.'}, status=503)
    except groq_lib.APIStatusError as e:
        return JsonResponse({'error': f'AI assistant error ({e.status_code}).'}, status=502)
    except Exception as e:
        print(f"GROQ ERROR: {str(e)}")
        return JsonResponse({'error': 'AI assistant is temporarily unavailable.'}, status=503)