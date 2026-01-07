from .models import Appointment
from django.utils import timezone
from datetime import datetime

def is_slot_available(gp, date, start_time, end_time):
    """Check if a GP slot is available (no conflicting appointments)"""
    # Combine date and start_time into a datetime
    appointment_datetime = timezone.make_aware(datetime.combine(date, start_time))
    
    # gp is a GP object, we need the User object for the query
    doctor_user = gp.user if hasattr(gp, 'user') else gp
    
    conflicts = Appointment.objects.filter(
        doctor=doctor_user,
        appointment_date=appointment_datetime,
        status='confirmed'  # Only check confirmed appointments
    )
    
    return not conflicts.exists()
