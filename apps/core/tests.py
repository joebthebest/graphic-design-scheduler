from django.test import TestCase, Client
from django.urls import reverse
from .models import ContactInquiry


class CoreAppTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_pages_render_successfully(self):
        urls = ['home', 'portfolio', 'services', 'about', 'contact']
        for url_name in urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200, f"Page {url_name} failed to load.")

    def test_contact_inquiry_submission(self):
        post_data = {
            'name': 'Test Client',
            'email': 'client@brand.com',
            'phone': '+234 810 000 0000',
            'subject': 'Logo Rebranding',
            'message': 'We are looking for a complete luxury visual overhaul for our beauty brand.'
        }
        response = self.client.post(reverse('contact'), data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactInquiry.objects.count(), 1)
        inquiry = ContactInquiry.objects.first()
        self.assertEqual(inquiry.name, 'Test Client')
        self.assertEqual(inquiry.subject, 'Logo Rebranding')
