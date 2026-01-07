from django.db import models
from django.conf import settings

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
        ordering = ['date','start_time']
        unique_together = ('gp','date','start_time','end_time')

    def __str__(self):
        return f"{self.gp} {self.date} {self.start_time}-{self.end_time}"

class Appointment(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    gp = models.ForeignKey(GP, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date','start_time']

    def __str__(self):
        return f"{self.patient.username} - {self.date} {self.start_time}"

    def overlaps(self, other_start, other_end):
        return self.start_time < other_end and self.end_time > other_start
