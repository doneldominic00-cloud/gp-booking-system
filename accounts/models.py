from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPES = (
        ('patient', 'Patient'),
        ('admin', 'Admin Staff'),
        ('gp', 'GP Doctor'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='patient')

    def is_patient(self):
        return self.user_type == 'patient'

    def is_admin_staff(self):
        return self.user_type == 'admin'

    def is_gp(self):
        return self.user_type == 'gp'
