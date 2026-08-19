from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date, time, timedelta

from apps.scheduling.models import Service, PortfolioItem, WorkingHours, BlackoutDate, Appointment, Review
from apps.scheduling.utils import get_available_slots, generate_ics_content


class SchedulingTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.service = Service.objects.create(
            name="Brand Identity & Logo Suite",
            slug="brand-identity-logo-suite",
            category="branding",
            duration_minutes=60,
            buffer_minutes=15,
            price=150000.00,
            currency="₦",
            is_active=True
        )

        # Set up working hours for Mon-Fri
        for day in range(5):
            WorkingHours.objects.create(
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                break_start=time(13, 0),
                break_end=time(14, 0),
                is_off=False
            )
        # Sunday is OFF
        WorkingHours.objects.create(
            day_of_week=6,
            start_time=time(9, 0),
            end_time=time(17, 0),
            is_off=True
        )

        # Create admin user
        self.admin_user = User.objects.create_superuser("admin", "admin@studio.com", "admin123")

    def test_service_creation(self):
        self.assertEqual(self.service.name, "Brand Identity & Logo Suite")
        self.assertEqual(self.service.slug, "brand-identity-logo-suite")
        self.assertEqual(str(self.service), "Brand Identity & Logo Suite (₦150000.00)")

    def test_available_slots_calculation(self):
        # Pick a future Monday
        today = timezone.localdate()
        days_ahead = (0 - today.weekday()) % 7
        if days_ahead <= 0:
            days_ahead += 7
        future_monday = today + timedelta(days=days_ahead)

        slots = get_available_slots(self.service, future_monday)
        self.assertTrue(len(slots) > 0)
        
        # Verify first slot starts at 09:00
        self.assertEqual(slots[0]['start_time'], '09:00')

        # Check lunch break (13:00 - 14:00) is excluded
        for slot in slots:
            self.assertNotEqual(slot['start_time'], '13:00')
            self.assertNotEqual(slot['start_time'], '13:30')

    def test_double_booking_prevention(self):
        today = timezone.localdate()
        days_ahead = (0 - today.weekday()) % 7
        if days_ahead <= 0:
            days_ahead += 7
        future_monday = today + timedelta(days=days_ahead)

        # Create appointment at 09:00 to 10:00
        Appointment.objects.create(
            service=self.service,
            client_name="John Doe",
            client_email="john@example.com",
            client_phone="+1234567890",
            appointment_date=future_monday,
            start_time=time(9, 0),
            end_time=time(10, 0),
            status="CONFIRMED"
        )

        # Fetch available slots again
        slots = get_available_slots(self.service, future_monday)
        slot_times = [s['start_time'] for s in slots]
        
        # 09:00 should no longer be available
        self.assertNotIn('09:00', slot_times)

    def test_booking_wizard_post(self):
        today = timezone.localdate()
        days_ahead = (1 - today.weekday()) % 7
        if days_ahead <= 0:
            days_ahead += 7
        future_tuesday = today + timedelta(days=days_ahead)

        payload = {
            'service': self.service.id,
            'appointment_date': future_tuesday.strftime('%Y-%m-%d'),
            'start_time': '10:00',
            'client_name': 'Jane Designer Client',
            'client_email': 'jane@brand.com',
            'client_phone': '+2348012345678',
            'company_or_brand': 'Jane Botanicals',
            'design_brief': 'Need a clean green and gold logo package.',
            'meeting_type': 'GOOGLE_MEET',
        }

        response = self.client.post(reverse('book_wizard'), data=payload)
        self.assertEqual(response.status_code, 302)

        # Check appointment was created
        appt = Appointment.objects.filter(client_email='jane@brand.com').first()
        self.assertIsNotNone(appt)
        self.assertTrue(appt.booking_reference.startswith('DES-'))

    def test_ics_generation(self):
        appt = Appointment.objects.create(
            service=self.service,
            client_name="Alice Smith",
            client_email="alice@test.com",
            client_phone="+1234567890",
            appointment_date=date(2026, 9, 15),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status="CONFIRMED"
        )
        ics_text = generate_ics_content(appt)
        self.assertIn("BEGIN:VCALENDAR", ics_text)
        self.assertIn("UID:DES-", ics_text)
        self.assertIn("alice@test.com", ics_text)
        self.assertIn("END:VCALENDAR", ics_text)

    def test_booking_lookup(self):
        appt = Appointment.objects.create(
            service=self.service,
            client_name="Bob Miller",
            client_email="bob@miller.com",
            client_phone="+1987654321",
            appointment_date=date(2026, 9, 20),
            start_time=time(11, 0),
            end_time=time(12, 0),
            status="CONFIRMED"
        )
        lookup_res = self.client.post(reverse('lookup_booking'), data={
            'booking_reference': appt.booking_reference,
            'client_email': 'bob@miller.com'
        })
        self.assertEqual(lookup_res.status_code, 302)
        self.assertIn(appt.booking_reference, lookup_res.url)

    def test_dashboard_permission_protection(self):
        # Unauthenticated user should be redirected to login
        res = self.client.get(reverse('designer_dashboard'))
        self.assertEqual(res.status_code, 302)
        self.assertIn(reverse('login'), res.url)

        # Logged in admin can access dashboard
        self.client.login(username="admin", password="admin123")
        res_auth = self.client.get(reverse('designer_dashboard'))
        self.assertEqual(res_auth.status_code, 200)
        self.assertContains(res_auth, "Designer Management Dashboard")
