from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    """Custom User model with role-based authentication"""
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    mobile = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"


class DoctorProfile(models.Model):
    """Extended profile for doctors"""
    SPECIALIZATION_CHOICES = (
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('psychiatry', 'Psychiatry'),
        ('oncology', 'Oncology'),
        ('gastroenterology', 'Gastroenterology'),
        ('urology', 'Urology'),
        ('gynecology', 'Gynecology'),
        ('ophthalmology', 'Ophthalmology'),
        ('otolaryngology', 'Otolaryngology (ENT)'),
        ('pulmonology', 'Pulmonology'),
        ('rheumatology', 'Rheumatology'),
        ('endocrinology', 'Endocrinology'),
        ('other', 'Other'),
    )
    
    QUALIFICATION_CHOICES = (
        ('mbbs', 'MBBS'),
        ('md', 'MD'),
        ('ms', 'MS'),
        ('dip', 'Diploma'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialization = models.CharField(max_length=100, choices=SPECIALIZATION_CHOICES)
    custom_specialization = models.CharField(max_length=100, blank=True, null=True)
    qualification = models.CharField(max_length=200, choices=QUALIFICATION_CHOICES)
    experience_years = models.IntegerField(default=0)
    registration_number = models.CharField(max_length=50, unique=True)
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='doctor_pics/', default='default_doctor.png')
    bio = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_ratings = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"
    
    def update_rating(self, new_rating):
        """Update doctor's average rating"""
        total = self.rating * self.total_ratings
        self.total_ratings += 1
        self.rating = (total + new_rating) / self.total_ratings
        self.save()


class PatientProfile(models.Model):
    """Extended profile for patients"""
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField()
    
    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    address = models.TextField()
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default_patient.png')
    emergency_contact = models.CharField(max_length=17)
    medical_history = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Patient"
    
   