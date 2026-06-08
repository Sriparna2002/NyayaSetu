from django.db import models

class Lawyer(models.Model):
    SPECIALIZATION_CHOICES = [
        ('Criminal', 'Criminal Law'),
        ('Civil', 'Civil Law'),
        ('Cyber', 'Cyber Law'),
        ('Corporate', 'Corporate Law'),
        ('Family', 'Family Law'),
        ('Property', 'Property Law'),
        ('Consumer', 'Consumer Law'),
        ('Labor', 'Labor Law'),
        ('Tax', 'Tax Law'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    # Professional Info
    degree = models.CharField(max_length=200, help_text="LLB, LLM, etc.")
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    experience = models.IntegerField(help_text="Years of experience")
    bio = models.TextField(blank=True, null=True)
    
    # Cases handled
    cases_handled = models.TextField(blank=True, null=True, help_text="Types of cases handled")
    
    # Evidence/Proof
    bar_council_id = models.CharField(max_length=50, unique=True)
    certificate = models.FileField(upload_to='lawyer_certificates/', blank=True, null=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    rating = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Adv. {self.name} - {self.specialization}"


class LawyerBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ]
    
    lawyer = models.ForeignKey(Lawyer, on_delete=models.CASCADE, related_name='bookings')
    client_name = models.CharField(max_length=100, default='')  # ← default যোগ করা হয়েছে
    client_email = models.EmailField(default='')  # ← default যোগ করা হয়েছে
    client_phone = models.CharField(max_length=15, default='')  # ← default যোগ করা হয়েছে
    case_type = models.CharField(max_length=100, default='')  # ← default যোগ করা হয়েছে
    case_description = models.TextField(default='')  # ← default যোগ করা হয়েছে
    preferred_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client_name} → {self.lawyer.name}"