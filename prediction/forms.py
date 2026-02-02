from django import forms
from .models import Symptom


class CustomSymptomForm(forms.Form):
    """Form for submitting custom/suggested symptoms"""
    symptom_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g., Dizziness, Bloating, etc.',
            'class': 'form-control'
        })
    )
    symptom_description = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Describe this symptom...',
            'class': 'form-control',
            'rows': 4
        })
    )

    def clean_symptom_name(self):
        symptom_name = self.cleaned_data['symptom_name'].strip()
        if len(symptom_name) < 2:
            raise forms.ValidationError("Symptom name must be at least 2 characters long.")
        if Symptom.objects.filter(name__iexact=symptom_name).exists():
            raise forms.ValidationError("This symptom already exists in our database.")
        return symptom_name
