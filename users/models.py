from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Admin'),
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # Override the email field to make it unique
    email = models.EmailField(_('email address'), unique=True)
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    
    class Meta:
        db_table = 'users'

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100)
    experience_years = models.IntegerField()
    qualification = models.CharField(max_length=200)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_ratings = models.IntegerField(default=0)
    available_days = models.JSONField(default=list)
    available_times = models.JSONField(default=list)
    
    class Meta:
        db_table = 'doctors'

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    medical_history = models.TextField(blank=True)
    
    class Meta:
        db_table = 'patients'

    def __str__(self):
        return self.user.get_full_name()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['timestamp']