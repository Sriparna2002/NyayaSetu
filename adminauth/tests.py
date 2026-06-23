from django.test import TestCase
from django.contrib.auth.models import User
from userauth.models import Complaint

class AdminAuthTests(TestCase):
    def test_admin_dashboard_url(self):
        response = self.client.get('/admin-dashboard/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirects to login


from userauth.models import PasswordReset
from django.urls import reverse

class AdminPasswordResetTest(TestCase):
    def setUp(self):
        # Admin user (is_staff=True)
        self.admin_user = User.objects.create_user(username='admin_user', email='admin@example.com', password='old_password123', is_staff=True)
        # Regular user (is_staff=False, is_superuser=False)
        self.citizen_user = User.objects.create_user(username='citizen_user', email='citizen@example.com', password='citizen_password')

    def test_admin_forgot_password_page_loads(self):
        response = self.client.get(reverse('admin_forgot_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_auth/admin_forgot_password.html')

    def test_admin_forgot_password_submits_valid_admin_email(self):
        response = self.client.post(reverse('admin_forgot_password'), {'email': 'admin@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_auth/admin_forgot_password.html')
        
        # Check that a PasswordReset token was created for admin
        reset_token = PasswordReset.objects.filter(user=self.admin_user, is_used=False).first()
        self.assertIsNotNone(reset_token)
        self.assertIn(str(reset_token.token), response.context['reset_link'])

    def test_admin_forgot_password_rejects_citizen_email(self):
        response = self.client.post(reverse('admin_forgot_password'), {'email': 'citizen@example.com'})
        self.assertEqual(response.status_code, 200)
        
        # Verify no token was created
        self.assertEqual(PasswordReset.objects.filter(user=self.citizen_user).count(), 0)

    def test_admin_reset_password_page_loads_with_valid_token(self):
        reset_obj = PasswordReset.objects.create(user=self.admin_user)
        response = self.client.get(reverse('admin_reset_password', kwargs={'token': reset_obj.token}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_auth/admin_reset_password.html')

    def test_admin_reset_password_page_redirects_with_invalid_token(self):
        import uuid
        response = self.client.get(reverse('admin_reset_password', kwargs={'token': uuid.uuid4()}))
        self.assertEqual(response.status_code, 302) # Redirects to admin_login

    def test_admin_reset_password_successful(self):
        reset_obj = PasswordReset.objects.create(user=self.admin_user)
        response = self.client.post(reverse('admin_reset_password', kwargs={'token': reset_obj.token}), {
            'new_password': 'new_admin_pass123',
            'confirm_password': 'new_admin_pass123'
        })
        self.assertEqual(response.status_code, 302) # Redirects to admin_login page
        
        # Verify PasswordReset record is marked used
        reset_obj.refresh_from_db()
        self.assertTrue(reset_obj.is_used)
        
        # Verify admin can log in with new password
        login_success = self.client.login(username='admin_user', password='new_admin_pass123')
        self.assertTrue(login_success)