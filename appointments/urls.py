from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('slots/', views.available_slots, name='available_slots'),
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
    path('book/success/<int:appt_id>/', views.book_success, name='book_success'),
    path('block/<int:slot_id>/', views.block_slot, name='block_slot'),
]
