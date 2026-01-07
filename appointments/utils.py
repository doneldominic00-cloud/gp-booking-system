from .models import Appointment

def is_slot_available(gp, date, start, end):
    conflicts = Appointment.objects.filter(
        gp=gp,
        date=date,
        start_time__lt=end,
        end_time__gt=start,
        cancelled=False
    )
    return not conflicts.exists()
