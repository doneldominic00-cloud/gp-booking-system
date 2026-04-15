from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from appointments.models import Appointment


class Command(BaseCommand):
    help = 'Send reminder emails to patients with confirmed appointments in the next 24 hours'

    def handle(self, *args, **options):
        now = timezone.now()
        window_start = now + timedelta(hours=23, minutes=30)
        window_end = now + timedelta(hours=24, minutes=30)

        upcoming = Appointment.objects.filter(
            status='confirmed',
            appointment_date__gte=window_start,
            appointment_date__lte=window_end,
        ).select_related('patient', 'doctor')

        if not upcoming.exists():
            self.stdout.write('No reminders to send.')
            return

        sent = 0
        failed = 0

        for appointment in upcoming:
            patient = appointment.patient
            patient_email = patient.email

            if not patient_email:
                self.stderr.write(
                    f'Skipping appointment {appointment.id}: patient {patient.get_full_name()} has no email address.'
                )
                failed += 1
                continue

            doctor_name = f'Dr. {appointment.doctor.get_full_name()}'
            appt_time = timezone.localtime(appointment.appointment_date)
            formatted_time = appt_time.strftime('%A, %d %B %Y at %H:%M')

            subject = 'Reminder: Your GP appointment tomorrow'
            message = (
                f'Dear {patient.get_full_name()},\n\n'
                f'This is a reminder that you have a confirmed appointment with {doctor_name} '
                f'on {formatted_time}.\n\n'
                f'Reason: {appointment.reason or "Not specified"}\n\n'
                f'Please arrive a few minutes early. If you need to cancel or reschedule, '
                f'contact the surgery as soon as possible.\n\n'
                f'Kind regards,\n'
                f'The GP Booking System'
            )

            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[patient_email],
                    fail_silently=False,
                )
                sent += 1
                self.stdout.write(
                    f'Reminder sent to {patient.get_full_name()} <{patient_email}> '
                    f'for appointment on {formatted_time}.'
                )
            except Exception as e:
                failed += 1
                self.stderr.write(
                    f'Failed to send reminder for appointment {appointment.id}: {e}'
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Done. {sent} reminder(s) sent, {failed} failed.'
            )
        )
