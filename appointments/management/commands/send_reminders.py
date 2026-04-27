from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from appointments.models import Appointment


class Command(BaseCommand):
    help = 'Send reminder emails for appointments in the next 24 hours'

    def handle(self, *args, **options):
        now = timezone.now()
        upcoming = Appointment.objects.filter(
            status='confirmed',
            appointment_date__gte=now + timedelta(hours=23, minutes=30),
            appointment_date__lte=now + timedelta(hours=24, minutes=30),
        ).select_related('patient', 'doctor')

        for appointment in upcoming:
            email = appointment.patient.email
            if not email:
                continue

            appt_time = timezone.localtime(appointment.appointment_date).strftime('%d %B %Y at %H:%M')
            send_mail(
                subject='Reminder: Your GP appointment tomorrow',
                message=(
                    f'Hi {appointment.patient.first_name},\n\n'
                    f'You have an appointment with Dr. {appointment.doctor.get_full_name()} on {appt_time}.\n\n'
                    f'Please arrive a few minutes early.\n\n'
                    f'GP Booking System'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )

        self.stdout.write(self.style.SUCCESS(f'Reminders sent for {upcoming.count()} appointment(s).'))
