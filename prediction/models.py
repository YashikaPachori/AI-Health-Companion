from django.db import models
from accounts.models import User, PatientProfile

class Disease(models.Model):
    """Disease information"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    severity_level = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('critical', 'Critical')
    ])
    specialist_required = models.CharField(max_length=100)  # e.g., Cardiologist, Gastroenterologist
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Symptom(models.Model):
    """Available symptoms for disease prediction"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class DiseasePrecaution(models.Model):
    """Precautions for each disease"""
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='precautions')
    precaution = models.TextField()
    priority = models.IntegerField(default=1)  # 1 = highest priority
    
    def __str__(self):
        return f"{self.disease.name} - Precaution {self.priority}"
    
    class Meta:
        ordering = ['priority']


class DiseaseDiet(models.Model):
    """Diet recommendations for each disease"""
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='diet_recommendations')
    food_item = models.CharField(max_length=200)
    is_recommended = models.BooleanField(default=True)  # True = eat, False = avoid
    description = models.TextField(blank=True)
    
    def __str__(self):
        status = "Recommended" if self.is_recommended else "Avoid"
        return f"{self.disease.name} - {status}: {self.food_item}"


class DiseaseExercise(models.Model):
    """Exercise recommendations for each disease"""
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='exercises')
    exercise_name = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.CharField(max_length=100)  # e.g., "30 minutes daily"
    intensity = models.CharField(max_length=20, choices=[
        ('light', 'Light'),
        ('moderate', 'Moderate'),
        ('vigorous', 'Vigorous')
    ])
    
    def __str__(self):
        return f"{self.disease.name} - {self.exercise_name}"


class DiseaseMedicine(models.Model):
    """Top medicine recommendations for each disease"""
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, related_name='medicines')
    medicine_name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    dosage = models.CharField(max_length=100)  # e.g., "500mg twice daily"
    description = models.TextField()
    side_effects = models.TextField(blank=True)
    priority = models.IntegerField(default=1)  # 1 = first choice
    
    def __str__(self):
        return f"{self.disease.name} - {self.medicine_name}"
    
    class Meta:
        ordering = ['priority']


class PredictionHistory(models.Model):
    """Store patient's disease prediction history"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='predictions')
    symptoms = models.TextField()  # JSON string of selected symptoms
    predicted_disease = models.ForeignKey(Disease, on_delete=models.SET_NULL, null=True, blank=True)
    disease_name = models.CharField(max_length=200, blank=True)  # used when predicted_disease is null (disease not in DB)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    patient_age = models.IntegerField()
    additional_notes = models.TextField(blank=True)
    consulted_doctor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        name = self.predicted_disease.name if self.predicted_disease else (self.disease_name or 'Unknown')
        return f"{self.patient.user.username} - {name} ({self.confidence_score}%)"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Prediction Histories'


class CustomSymptomSuggestion(models.Model):
    """Store patient suggestions for new symptoms"""
    symptom_name = models.CharField(max_length=200)
    symptom_description = models.TextField(blank=True)
    suggested_by = models.ForeignKey('accounts.PatientProfile', on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.symptom_name} - {'Approved' if self.is_approved else 'Pending'}"
    
    class Meta:
        ordering = ['-created_at']
