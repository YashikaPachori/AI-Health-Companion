from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, PatientProfile, DoctorProfile

class PatientSignUpForm(UserCreationForm):
    """Form for patient registration"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=17)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=PatientProfile.GENDER_CHOICES, widget=forms.Select)
    address = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'mobile', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email
    
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile and not mobile.replace('+', '').replace('-', '').isdigit():
            raise forms.ValidationError("Mobile number should contain only digits, + and -")
        return mobile
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'patient'
        user.email = self.cleaned_data['email']
        user.mobile = self.cleaned_data['mobile']
        if commit:
            user.save()
            # Create patient profile
            PatientProfile.objects.create(
                user=user,
                date_of_birth=self.cleaned_data['date_of_birth'],
                gender=self.cleaned_data['gender'],
                address=self.cleaned_data['address'],
                emergency_contact=self.cleaned_data['mobile']
            )
        return user


class DoctorSignUpForm(UserCreationForm):
    """Form for doctor registration"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    mobile = forms.CharField(max_length=17)
    specialization = forms.ChoiceField(choices=DoctorProfile.SPECIALIZATION_CHOICES, widget=forms.Select)
    custom_specialization = forms.CharField(max_length=100, required=False, help_text="Enter custom specialization if you selected 'Other'")
    qualification = forms.ChoiceField(choices=DoctorProfile.QUALIFICATION_CHOICES, widget=forms.Select)
    experience_years = forms.IntegerField(min_value=0)
    registration_number = forms.CharField(max_length=50)
    address = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'mobile', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email
    
    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if mobile and not mobile.replace('+', '').replace('-', '').isdigit():
            raise forms.ValidationError("Mobile number should contain only digits, + and -")
        return mobile
    
    def clean(self):
        cleaned_data = super().clean()
        specialization = cleaned_data.get('specialization')
        custom_specialization = cleaned_data.get('custom_specialization')
        
        if specialization == 'other' and not custom_specialization:
            raise forms.ValidationError("Please enter a custom specialization if you selected 'Other'.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'doctor'
        user.email = self.cleaned_data['email']
        user.mobile = self.cleaned_data['mobile']
        if commit:
            user.save()
            # Create doctor profile
            DoctorProfile.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                custom_specialization=self.cleaned_data.get('custom_specialization', ''),
                qualification=self.cleaned_data['qualification'],
                experience_years=self.cleaned_data['experience_years'],
                registration_number=self.cleaned_data['registration_number'],
                address=self.cleaned_data['address']
            )
        return user


class UserLoginForm(AuthenticationForm):
    """Custom login form"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class PatientProfileUpdateForm(forms.ModelForm):
    """Form for updating patient profile"""
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    mobile = forms.CharField(max_length=17)
    
    class Meta:
        model = PatientProfile
        fields = ['date_of_birth', 'gender', 'blood_group', 'address', 'profile_picture', 'emergency_contact', 'medical_history', 'allergies']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'medical_history': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['mobile'].initial = self.instance.user.mobile


class DoctorProfileUpdateForm(forms.ModelForm):
    """Form for updating doctor profile"""
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    mobile = forms.CharField(max_length=17)
    
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'custom_specialization', 'qualification', 'experience_years', 'address', 'profile_picture', 'bio', 'consultation_fee', 'is_available']
        widgets = {
            'specialization': forms.Select(choices=DoctorProfile.SPECIALIZATION_CHOICES),
            'qualification': forms.Select(choices=DoctorProfile.QUALIFICATION_CHOICES),
            'address': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['mobile'].initial = self.instance.user.mobile