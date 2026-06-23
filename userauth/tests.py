from django.test import TestCase
from django.contrib.auth.models import User
from .models import Complaint

class ComplaintPriorityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_urgent_priority_classification(self):
        description = "My life is in danger. A hacker has hacked my account and is blackmailing me with a weapon threat."
        complaint = Complaint.objects.create(
            user=self.user,
            category="Cyber Crime",
            description=description
        )
        self.assertEqual(complaint.priority, "Urgent")

    def test_medium_priority_classification(self):
        description = "There is a severe property dispute regarding illegal occupation of my land."
        complaint = Complaint.objects.create(
            user=self.user,
            category="Land/Property Dispute",
            description=description
        )
        self.assertEqual(complaint.priority, "Medium")

    def test_low_priority_classification(self):
        description = "I bought a TV online but the seller delivered a different brand and now refuses to reply to my messages."
        complaint = Complaint.objects.create(
            user=self.user,
            category="Consumer Dispute",
            description=description
        )
        self.assertEqual(complaint.priority, "Low")

    def test_manual_priority_override_on_update(self):
        # Initial creation should auto-classify to Urgent
        complaint = Complaint.objects.create(
            user=self.user,
            category="Police Complaint",
            description="Emergency! Someone stole my car and is threatening me."
        )
        self.assertEqual(complaint.priority, "Urgent")
        
        # Admin updates priority to Low, saving should NOT overwrite the admin override
        complaint.priority = "Low"
        complaint.save()
        
        # Fetch from DB and check
        updated_complaint = Complaint.objects.get(id=complaint.id)
        self.assertEqual(updated_complaint.priority, "Low")


from .models import PasswordReset
from django.urls import reverse
from django.utils import timezone

class PasswordResetTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='citizen_user', email='citizen@example.com', password='old_password123')

    def test_forgot_password_page_loads(self):
        response = self.client.get(reverse('forgot_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/forgot_password.html')

    def test_forgot_password_submits_valid_email(self):
        response = self.client.post(reverse('forgot_password'), {'email': 'citizen@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/forgot_password.html')
        
        # Check that a PasswordReset token was created
        reset_token = PasswordReset.objects.filter(user=self.user, is_used=False).first()
        self.assertIsNotNone(reset_token)
        self.assertIn(str(reset_token.token), response.context['reset_link'])

    def test_forgot_password_submits_invalid_email(self):
        response = self.client.post(reverse('forgot_password'), {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 200)
        
        # Verify no token was created
        self.assertEqual(PasswordReset.objects.count(), 0)

    def test_reset_password_page_loads_with_valid_token(self):
        reset_obj = PasswordReset.objects.create(user=self.user)
        response = self.client.get(reverse('reset_password', kwargs={'token': reset_obj.token}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/reset_password.html')

    def test_reset_password_page_redirects_with_invalid_token(self):
        import uuid
        response = self.client.get(reverse('reset_password', kwargs={'token': uuid.uuid4()}))
        self.assertEqual(response.status_code, 302) # Redirects to login

    def test_reset_password_successful(self):
        reset_obj = PasswordReset.objects.create(user=self.user)
        response = self.client.post(reverse('reset_password', kwargs={'token': reset_obj.token}), {
            'new_password': 'new_password123',
            'confirm_password': 'new_password123'
        })
        self.assertEqual(response.status_code, 302) # Redirects to login page
        
        # Verify PasswordReset record is marked used
        reset_obj.refresh_from_db()
        self.assertTrue(reset_obj.is_used)
        
        # Verify user can log in with new password
        login_success = self.client.login(username='citizen_user', password='new_password123')
        self.assertTrue(login_success)

