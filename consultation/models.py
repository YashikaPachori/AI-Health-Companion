
from django.db import models
from accounts.models import PatientProfile, DoctorProfile
from prediction.models import PredictionHistory

class Consultation(models.Model):
    """Consultation between patient and doctor"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    )
    
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='consultations')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='consultations')
    prediction = models.ForeignKey(PredictionHistory, on_delete=models.SET_NULL, null=True, blank=True)
    
    chief_complaint = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    consultation_date = models.DateTimeField(auto_now_add=True)
    closed_date = models.DateTimeField(null=True, blank=True)
    
    diagnosis = models.TextField(blank=True)
    prescription = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.user.username} - Dr. {self.doctor.user.last_name} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']


class ChatMessage(models.Model):
    """Chat messages between patient and doctor"""
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.username}: {self.message[:50]}"
    
    class Meta:
        ordering = ['created_at']


class DoctorRating(models.Model):
    """Patient ratings and feedback for doctors"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='given_ratings')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='received_ratings')
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='rating')
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient.user.username} rated Dr. {self.doctor.user.last_name}: {self.rating}/5"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update doctor's rating
        self.doctor.update_rating(self.rating)
    
    class Meta:
        unique_together = ['patient', 'consultation']
# Create your models here.
