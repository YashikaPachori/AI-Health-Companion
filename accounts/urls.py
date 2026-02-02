from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('signup/patient/', views.patient_signup, name='patient_signup'),
    path('signup/doctor/', views.doctor_signup, name='doctor_signup'),
    path('signin/', views.signin_view, name='signin'),
    path('signin/patient/', views.patient_login, name='patient_login'),
    path('signin/doctor/', views.doctor_login, name='doctor_login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profiles
    path('patient/<str:username>/', views.patient_profile, name='patient_profile'),
    path('doctor/<str:username>/', views.doctor_profile, name='doctor_profile'),
    path('patient/<str:username>/edit/', views.edit_patient_profile, name='edit_patient_profile'),
    path('doctor/<str:username>/edit/', views.edit_doctor_profile, name='edit_doctor_profile'),
]
