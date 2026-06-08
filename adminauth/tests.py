from django.test import TestCase
from django.contrib.auth.models import User
from userauth.models import Complaint

class AdminAuthTests(TestCase):
    def test_admin_dashboard_url(self):
        response = self.client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirects to login