from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    path('check-symptoms/', views.check_symptoms, name='check_symptoms'),
    path('predict/', views.predict_disease_view, name='predict_disease'),
    path('result/', views.disease_result, name='disease_result'),
    path('disease/<str:disease_name>/', views.disease_detail, name='disease_detail'),
    path('history/', views.prediction_history, name='prediction_history'),
    path('add-custom-symptom/', views.add_custom_symptom, name='add_custom_symptom'),
]