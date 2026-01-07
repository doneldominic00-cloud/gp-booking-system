from django.db import models
from django.conf import settings
from django.utils import timezone


class GP(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    speciality = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"


class GPAvailability(models.Model):
    gp = models.ForeignKey(GP, on_delete=models.CASCADE, related_name='availabilities')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_blocked = models.BooleanField(default=False)

    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ('gp', 'date', 'start_time', 'end_time')
        verbose_name_plural = 'GP Availabilities'

    def __str__(self):
        return f"{self.gp} - {self.date} {self.start_time}-{self.end_time}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments'
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'user_type': 'doctor'}
    )
    appointment_date = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date']

    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.doctor.get_full_name()} - {self.appointment_date}"
