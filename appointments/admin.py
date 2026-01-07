from django.contrib import admin
from .models import GP, GPAvailability, Appointment


@admin.register(GP)
class GPAdmin(admin.ModelAdmin):
    list_display = ('user', 'speciality')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'speciality')
    list_filter = ('speciality',)


@admin.register(GPAvailability)
class GPAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('gp', 'date', 'start_time', 'end_time', 'is_blocked')
    list_filter = ('date', 'gp', 'is_blocked')
    search_fields = ('gp__user__username', 'gp__user__first_name', 'gp__user__last_name')
    date_hierarchy = 'date'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'status', 'created_at']
    list_filter = ['status', 'appointment_date']
    search_fields = ['patient__email', 'doctor__email', 'reason']
