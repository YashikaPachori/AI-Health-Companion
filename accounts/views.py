
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PatientSignUpForm, DoctorSignUpForm, UserLoginForm, PatientProfileUpdateForm, DoctorProfileUpdateForm
from .models import User, PatientProfile, DoctorProfile

def signup_view(request):
    """Display signup options (Patient/Doctor)"""
    return render(request, 'accounts/signup.html')


def patient_signup(request):
    """Patient registration"""
    form = PatientSignUpForm()
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:patient_profile', username=user.username)
    return render(request, 'accounts/patient_signup.html', {'form': form})


def doctor_signup(request):
    """Doctor registration"""
    form = DoctorSignUpForm()
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Doctor account created successfully!')
            return redirect('accounts:doctor_profile', username=user.username)
    return render(request, 'accounts/doctor_signup.html', {'form': form})


def signin_view(request):
    """Display signin options (Patient/Doctor/Admin)"""
    return render(request, 'accounts/signin.html')


def patient_login(request):
    """Patient login"""
    form = UserLoginForm(request)
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.user_type == 'patient':
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('accounts:patient_profile', username=user.username)
    return render(request, 'accounts/patient_login.html', {'form': form})


def doctor_login(request):
    """Doctor login"""
    form = UserLoginForm(request)
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.user_type == 'doctor':
                login(request, user)
                messages.success(request, f'Welcome back, Dr. {user.last_name}!')
                return redirect('accounts:doctor_profile', username=user.username)
    return render(request, 'accounts/doctor_login.html', {'form': form})


@login_required
def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def patient_profile(request, username):
    """View patient profile"""
    user = get_object_or_404(User, username=username)
    if user.user_type != 'patient':
        messages.error(request, 'Invalid profile.')
        return redirect('home')
    
    try:
        profile = user.patient_profile
    except Exception as e:
        # Try to create profile if it doesn't exist
        try:
            profile = PatientProfile.objects.create(
                user=user,
                date_of_birth=user.date_joined.date(),
                gender='other',
                address='Not provided',
                emergency_contact=user.mobile or 'Not provided'
            )
            messages.info(request, 'Profile created. Please update your information.')
        except Exception as e:
            messages.error(request, f'Error loading profile: {str(e)}')
            return redirect('home')
    
    context = {
        'user': user,
        'profile': profile,
        'is_owner': request.user == user,
    }
    return render(request, 'accounts/patient_profile.html', context)
    

@login_required
def doctor_profile(request, username):
    """View doctor profile"""
    user = get_object_or_404(User, username=username)
    if user.user_type != 'doctor':
        messages.error(request, 'Invalid profile.')
        return redirect('home')
    
    try:
        profile = user.doctor_profile
    except Exception as e:
        # Try to create profile if it doesn't exist
        try:
            profile = DoctorProfile.objects.create(
                user=user,
                specialization='general_practice',
                qualification='mbbs',
                experience_years=0,
                registration_number=f'REG-{user.id}',
                address='Not provided'
            )
            messages.info(request, 'Profile created. Please update your information.')
        except Exception as e:
            messages.error(request, f'Error loading profile: {str(e)}')
            return redirect('home')
    
    context = {
        'user': user,
        'profile': profile,
        'is_owner': request.user == user,
    }
    return render(request, 'accounts/doctor_profile.html', context)


@login_required
def edit_patient_profile(request, username):
    """Edit patient profile"""
    user = get_object_or_404(User, username=username)
    if request.user != user or user.user_type != 'patient':
        messages.error(request, 'You cannot edit this profile.')
        return redirect('home')
    
    try:
        profile = user.patient_profile
    except PatientProfile.DoesNotExist:
        # Auto-create profile if missing
        profile = PatientProfile.objects.create(
            user=user,
            date_of_birth=user.date_joined.date(),
            gender='other',
            address='Not provided',
            emergency_contact=user.mobile or 'Not provided'
        )
        messages.info(request, 'Profile created. Please update your information.')
    
    form = PatientProfileUpdateForm(instance=profile)

    if request.method == 'POST':
        form = PatientProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update user info
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.mobile = form.cleaned_data['mobile']
            user.save()
            
            # Update and save profile
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:patient_profile', username=user.username)
    
    context = {
        'form': form,
        'user': user,
        'profile': profile,
        'is_edit': True
    }
    return render(request, 'accounts/patient_profile.html', context)


@login_required
def edit_doctor_profile(request, username):
    """Edit doctor profile"""
    user = get_object_or_404(User, username=username)
    if request.user != user or user.user_type != 'doctor':
        messages.error(request, 'You cannot edit this profile.')
        return redirect('home')
    
    try:
        profile = user.doctor_profile
    except DoctorProfile.DoesNotExist:
        # Auto-create profile if missing
        profile = DoctorProfile.objects.create(
            user=user,
            specialization='general_practice',
            qualification='mbbs',
            experience_years=0,
            registration_number=f'REG-{user.id}',
            address='Not provided'
        )
        messages.info(request, 'Profile created. Please update your information.')
    
    form = DoctorProfileUpdateForm(instance=profile)

    if request.method == 'POST':
        form = DoctorProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update user info
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.mobile = form.cleaned_data['mobile']
            user.save()
            
            # Update and save profile
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:doctor_profile', username=user.username)
    
    context = {
        'form': form,
        'user': user,
        'profile': profile,
        'is_edit': True
    }
    return render(request, 'accounts/doctor_profile.html', context)

# Create your views here.
