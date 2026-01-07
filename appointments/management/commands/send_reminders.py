from django.core.management.base import BaseCommand
from appointments.models import Appointment
from django.utils import timezone
from django.core.mail import send_mail
from datetime import timedelta

class Command(BaseCommand):
    help = "Send email reminders 24 hours before appointments"

    def handle(self, *args, **options):
        now = timezone.localdate()
        target_date = now + timedelta(days=1)
        appts = Appointment.objects.filter(date=target_date, cancelled=False)
        for a in appts:
            if a.patient.email:
                send_mail(
                    f"Reminder: appointment on {a.date}",
                    f"Dear {a.patient.first_name}, this is a reminder for your appointment with {a.gp} on {a.date} at {a.start_time}.",
                    None,
                    [a.patient.email],
                    fail_silently=True
                )
                self.stdout.write(f"Reminder sent to {a.patient.email} for appointment {a.id}")
