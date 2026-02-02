from django import forms
from .models import Consultation, ChatMessage, DoctorRating

class ConsultationRequestForm(forms.ModelForm):
    """Form for patients to request consultation"""
    class Meta:
        model = Consultation
        fields = ['chief_complaint']
        widgets = {
            'chief_complaint': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe your health concern...'
            })
        }


class ChatMessageForm(forms.ModelForm):
    """Form for sending chat messages"""
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Type a message...'
            })
        }


class DoctorRatingForm(forms.ModelForm):
    """Form for rating doctors"""
    class Meta:
        model = DoctorRating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'review': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Share your experience (optional)...'
            })
        }


class ConsultationUpdateForm(forms.ModelForm):
    """Form for doctors to update consultation"""
    class Meta:
        model = Consultation
        fields = ['status', 'diagnosis', 'prescription', 'doctor_notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'prescription': forms.Textarea(attrs={'rows': 4}),
            'doctor_notes': forms.Textarea(attrs={'rows': 3}),
        }