from django.contrib import admin
from django.urls import path, include
from appointments.views import home
admin.site.site_header = "GP Booking System Administration"
admin.site.site_title = "GP Booking Admin"
admin.site.index_title = "Welcome to the GP Booking System"
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('appointments/', include('appointments.urls')),
    path('', home, name='home'),
]
