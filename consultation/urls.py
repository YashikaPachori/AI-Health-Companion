from django.urls import path
from . import views

app_name = 'consultation'

urlpatterns = [
    # Doctor consultation
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('consult/<int:doctor_id>/', views.consult_doctor, name='consult_doctor'),
    path('consultation/<int:consultation_id>/', views.consultation_view, name='consultation_view'),
    path('consultation/<int:consultation_id>/close/', views.close_consultation, name='close_consultation'),
    path('consultation/<int:consultation_id>/resume/', views.resume_consultation, name='resume_consultation'),
    path('history/', views.consultation_history, name='consultation_history'),
    
    # Rating
    path('consultation/<int:consultation_id>/rate/', views.rate_doctor, name='rate_doctor'),
    
    # AJAX endpoints
    path('send-message/', views.send_message_ajax, name='send_message_ajax'),
    path('consultation/<int:consultation_id>/messages/', views.get_messages_ajax, name='get_messages_ajax'),
]