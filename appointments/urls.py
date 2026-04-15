from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('available-slots/', views.calendar_view, name='available_slots'),
    path('slots/', views.slots_feed, name='slots_feed'),
    path('api/book/<str:slot_id>/', views.book_slot_api, name='book_slot_api'),
    path('manage/', views.manage_availability, name='manage_availability'),
    path('manage/add/', views.add_availability, name='add_availability'),
    path('manage/block/<int:slot_id>/', views.block_slot, name='block_slot'),
    path('api/chat/', views.ai_chat_api, name='ai_chat'),
]
