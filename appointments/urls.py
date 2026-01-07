from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('available-slots/', views.calendar_view, name='available_slots'),
    path('slots/', views.slots_feed, name='slots_feed'),
    path('api/book/<str:slot_id>/', views.book_slot_api, name='book_slot_api'),
]
