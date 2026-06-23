from django.db import models
from django.contrib.auth.models import User
import time
import random

class Complaint(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
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
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Low')
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
    
    def classify_priority(self, text):
        if not text:
            return 'Low'
        
        text_lower = text.lower()
        
        # Urgent keywords - immediate physical, cybersecurity, or severe harassment risks
        urgent_keywords = [
            'kill', 'murder', 'threat', 'violence', 'assault', 'attack', 'kidnap', 
            'weapon', 'gun', 'pistol', 'knife', 'bomb', 'abuse', 'harass', 'stalk', 
            'acid', 'rape', 'molest', 'domestic violence', 'suicide', 'danger', 
            'beating', 'extortion', 'blackmail', 'hacked', 'hack', 'ransom', 'ransomware',
            'unauthorized transaction', 'identity theft', 'immediate assistance', 'emergency'
        ]
        
        # Medium keywords - property disputes, moderate financial fraud, theft, missing persons
        medium_keywords = [
            'land grab', 'illegal occupation', 'trespass', 'boundary dispute', 
            'property dispute', 'encroachment', 'tenant', 'landlord', 'eviction', 
            'deed', 'ownership', 'cheque bounce', 'cheat', 'breach of contract', 
            'fraudulent', 'stolen', 'theft', 'missing person', 'robbery', 'burglary',
            'unpaid salary', 'financial fraud'
        ]
        
        # Check for urgent keywords first
        for kw in urgent_keywords:
            if kw in text_lower:
                return 'Urgent'
                
        # Check for medium keywords next
        for kw in medium_keywords:
            if kw in text_lower:
                return 'Medium'
                
        return 'Low'

    def save(self, *args, **kwargs):
        if not self.complaint_id:
            timestamp = int(time.time() * 1000) % 100000
            random_num = random.randint(100, 999)
            self.complaint_id = f"NY-{timestamp}{random_num}"
            # Automatically classify priority based on description
            self.priority = self.classify_priority(self.description)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.complaint_id} - {self.user.username}"


import uuid
from django.utils import timezone
from datetime import timedelta

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=1)

    def __str__(self):
        return f"Reset token for {self.user.username}"