from django.contrib import admin
from .models import GP, GPAvailability, Appointment

@admin.register(GP)
class GPAdmin(admin.ModelAdmin):
    list_display = ('user','speciality')
    search_fields = ('user__username','user__first_name','user__last_name')

@admin.register(GPAvailability)
class GPAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('gp','date','start_time','end_time','is_blocked')
    list_filter = ('date','gp','is_blocked')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient','gp','date','start_time','cancelled')
    list_filter = ('date','cancelled')
