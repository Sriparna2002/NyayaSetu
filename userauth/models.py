from django.db import models
from django.contrib.auth.models import User
import time
import random

class Complaint(models.Model):
    PRIORITY_CHOICES = [
        ('Normal', 'Normal'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    ]
    
    CATEGORY_CHOICES = [
        ('Cyber Crime', 'Cyber Crime'),
        ('Consumer Dispute', 'Consumer Dispute'),
        ('Police Complaint', 'Police Complaint'),
        ('Land/Property Dispute', 'Land/Property Dispute'),
        ('Corporate/Legal', 'Corporate/Legal'),
        ('Other', 'Other'),
    ]
    
    complaint_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Normal')
    description = models.TextField()
    evidence = models.TextField(blank=True, null=True)
    evidence_name = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints')
    remarks = models.TextField(blank=True, null=True)
    
    # এই ফিল্ডটি যোগ করুন
    nearest_police_station = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nearest Police Station")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.complaint_id:
            timestamp = int(time.time() * 1000) % 100000
            random_num = random.randint(100, 999)
            self.complaint_id = f"NY-{timestamp}{random_num}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.complaint_id} - {self.user.username}"