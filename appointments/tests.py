from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from .models import GP, GPAvailability, Appointment
import datetime
import json

class BookingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='pat', 
            password='pass', 
            user_type='patient', 
            email='pat@example.com'
        )
        gp_user = User.objects.create_user(
            username='doc', 
            password='pass', 
            user_type='gp', 
            first_name='John', 
            last_name='Doe'
        )
        self.gp = GP.objects.create(user=gp_user)
        self.slot = GPAvailability.objects.create(
            gp=self.gp, 
            date=timezone.localdate() + datetime.timedelta(days=2), 
            start_time=datetime.time(10, 0), 
            end_time=datetime.time(10, 15)
        )

    def test_booking_creates_appointment_and_blocks_slot(self):
        self.client.login(username='pat', password='pass')
        resp = self.client.post(
            f'/appointments/api/book/{self.slot.id}/',
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_blocked)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_slot_is_blocked_after_booking(self):
        self.client.login(username='pat', password='pass')
        self.client.post(
            f'/appointments/api/book/{self.slot.id}/',
            content_type='application/json'
        )
        # Try booking the same slot again
        resp = self.client.post(
            f'/appointments/api/book/{self.slot.id}/',
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 404)

    def test_unauthenticated_user_cannot_book(self):
        resp = self.client.post(
            f'/appointments/api/book/{self.slot.id}/',
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 302)  # Redirects to login

    def test_is_patient_returns_true(self):
        self.assertTrue(self.user.is_patient())

    def test_is_gp_returns_true(self):
        gp_user = User.objects.get(username='doc')
        self.assertTrue(gp_user.is_gp())