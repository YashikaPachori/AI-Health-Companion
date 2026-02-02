from urllib.parse import unquote

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from .models import Symptom, Disease, PredictionHistory
from .ml_model import (
    predict_disease,
    get_disease_recommendations,
    get_fallback_disease_info,
    get_fallback_recommendations,
)
from accounts.models import DoctorProfile
from datetime import date


@login_required
def check_symptoms(request):
    """Main symptom checker page"""
    if request.user.user_type != 'patient':
        messages.error(request, 'Only patients can check symptoms.')
        return redirect('home')

    symptoms = Symptom.objects.all()

    return render(
        request,
        'prediction/check_symptoms.html',
        {'symptoms': symptoms}
    )


@login_required
@require_POST
def predict_disease_view(request):
    """Process symptoms and predict disease"""
    if request.user.user_type != 'patient':
        return JsonResponse(
            {'error': 'Only patients can use this feature'},
            status=403
        )

    try:
        data = json.loads(request.body)
        selected_symptoms = data.get('symptoms', [])

        # Normalize payload: support list of raw strings, objects like {value: 'x'},
        # or accidentally-serialized DOM-like objects from older templates.
        if not isinstance(selected_symptoms, list):
            return JsonResponse({'error': 'Invalid symptoms payload'}, status=400)

        cleaned_symptoms = []
        for item in selected_symptoms:
            # if client sent checkbox elements as objects, try common fields
            if isinstance(item, dict):
                # check common keys
                val = item.get('value') or item.get('name') or item.get('text')
                if val is None:
                    # fallback to string representation
                    val = str(item)
                cleaned_symptoms.append(str(val))
            else:
                # ensure it's a string
                cleaned_symptoms.append(str(item))

        # Remove empty strings and duplicates
        selected_symptoms = [s for s in map(lambda x: x.strip(), cleaned_symptoms) if s]

        if not selected_symptoms:
            return JsonResponse({'error': 'Please select at least one symptom'}, status=400)

        # Predict disease using ML model
        prediction = predict_disease(selected_symptoms)

        if not prediction:
            return JsonResponse(
                {'error': 'Could not predict disease. Please select at least two symptoms for a reliable prediction.'},
                status=400
            )

        patient_profile = getattr(request.user, 'patient_profile', None)

        disease_obj = (
            prediction['disease']
            if isinstance(prediction.get('disease'), Disease)
            else None
        )
        disease_name_str = (
            disease_obj.name if disease_obj else prediction.get('disease_name', '')
        )

        # Save prediction history if we can identify a patient profile.
        # Some users may have `user_type='patient'` but no PatientProfile object yet;
        # in that case skip saving to avoid a server error.
        patient_age = 0
        if patient_profile:
            try:
                dob = getattr(patient_profile, 'date_of_birth', None)
                today = date.today()
                patient_age = (
                    today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                ) if dob else 0
            except Exception:
                patient_age = 0

            PredictionHistory.objects.create(
                patient=patient_profile,
                symptoms=json.dumps(selected_symptoms),
                predicted_disease=disease_obj,
                disease_name=disease_name_str,
                confidence_score=prediction.get('confidence'),
                patient_age=patient_age
            )

        # Get recommendations - always return a structure, even if empty
        recommendations = (
            get_disease_recommendations(disease_obj)
            if disease_obj else {
                'precautions': [],
                'diet': {'recommended': [], 'avoid': []},
                'exercises': [],
                'medicines': []
            }
        )

        # Calculate patient age for response
        try:
            dob = patient_profile.date_of_birth
            today = date.today()
            patient_age = (
                today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            ) if dob else 0
        except Exception:
            patient_age = 0

        response_data = {
            'disease_name': (
                disease_obj.name
                if disease_obj else prediction.get('disease_name')
            ),
            'confidence': prediction.get('confidence'),
            'severity': prediction.get('severity'),
            'specialist': prediction.get('specialist'),
            'patient_name': request.user.get_full_name(),
            'patient_age': patient_age,
            'recommendations': recommendations,
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def disease_result(request):
    """Show disease prediction result with recommendations"""
    if request.user.user_type != 'patient':
        messages.error(request, 'Only patients can view results.')
        return redirect('home')

    try:
        latest_prediction = (
            request.user.patient_profile.predictions.latest('created_at')
        )
        disease = latest_prediction.predicted_disease
        if not disease and latest_prediction.disease_name:
            disease = get_fallback_disease_info(latest_prediction.disease_name)
        if not disease:
            messages.warning(
                request,
                'Your latest prediction could not be loaded. Please check symptoms again.'
            )
            return redirect('prediction:check_symptoms')

        if latest_prediction.predicted_disease:
            recommendations = get_disease_recommendations(disease)
        else:
            recommendations = get_fallback_recommendations(latest_prediction.disease_name or '')

        doctors = DoctorProfile.objects.filter(
            specialization__icontains=disease.specialist_required,
            is_available=True
        )

        context = {
            'prediction': latest_prediction,
            'disease': disease,
            'recommendations': recommendations,
            'doctors': doctors,
        }

        return render(
            request,
            'prediction/prediction_result.html',
            context
        )

    except PredictionHistory.DoesNotExist:
        messages.error(request, 'No prediction found. Check your symptoms first.')
        return redirect('prediction:check_symptoms')


@login_required
def disease_detail(request, disease_name):
    """Show detailed information about a disease (from DB or fallback)."""
    name = unquote(disease_name).strip()
    if not name:
        messages.error(request, 'Disease name is missing.')
        return redirect('prediction:check_symptoms')

    disease = Disease.objects.filter(name__iexact=name).first()

    if disease:
        recommendations = get_disease_recommendations(disease)
    else:
        # Use fallback info so every predicted disease has a page
        disease = get_fallback_disease_info(name)
        if not disease:
            messages.error(
                request,
                f'Information for "{name}" is not available. Please consult a doctor.'
            )
            return redirect('prediction:check_symptoms')
        recommendations = get_fallback_recommendations(name)

    doctors = DoctorProfile.objects.filter(
        specialization__icontains=disease.specialist_required,
        is_available=True
    )

    context = {
        'disease': disease,
        'recommendations': recommendations,
        'doctors': doctors,
    }

    return render(
        request,
        'prediction/prediction_detail.html',
        context
    )


@login_required
def prediction_history(request):
    """View patient's prediction history"""
    if request.user.user_type != 'patient':
        messages.error(
            request,
            'Only patients can view prediction history.'
        )
        return redirect('home')

    predictions = request.user.patient_profile.predictions.all()

    context = {
        'predictions': predictions,
    }

    return render(
        request,
        'prediction/prediction_history.html',
        context
    )

@login_required
@require_POST
def add_custom_symptom(request):
    """Allow patients to suggest new symptoms"""
    if request.user.user_type != 'patient':
        return JsonResponse(
            {'success': False, 'message': 'Only patients can submit symptom suggestions'},
            status=403
        )
    
    try:
        data = json.loads(request.body)
        symptom_name = data.get('symptom_name', '').strip()
        symptom_description = data.get('symptom_description', '').strip()
        
        if not symptom_name:
            return JsonResponse(
                {'success': False, 'message': 'Please enter a symptom name'},
                status=400
            )
        
        if len(symptom_name) < 2:
            return JsonResponse(
                {'success': False, 'message': 'Symptom name must be at least 2 characters long'},
                status=400
            )
        
        # Check if symptom already exists
        from .models import CustomSymptomSuggestion
        if Symptom.objects.filter(name__iexact=symptom_name).exists():
            return JsonResponse(
                {'success': False, 'message': 'This symptom already exists in our database'},
                status=400
            )
        
        # Check if this exact suggestion was already made recently
        from datetime import timedelta
        from django.utils import timezone
        recent_duplicate = CustomSymptomSuggestion.objects.filter(
            symptom_name__iexact=symptom_name,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).exists()
        
        if recent_duplicate:
            return JsonResponse(
                {'success': False, 'message': 'This symptom suggestion was recently submitted. Thank you for your interest!'},
                status=400
            )
        
        # Create the suggestion
        patient_profile = request.user.patient_profile if hasattr(request.user, 'patient_profile') else None
        CustomSymptomSuggestion.objects.create(
            symptom_name=symptom_name,
            symptom_description=symptom_description,
            suggested_by=patient_profile
        )
        
        return JsonResponse(
            {'success': True, 'message': 'Thank you for your suggestion!'},
            status=201
        )
        
    except json.JSONDecodeError:
        return JsonResponse(
            {'success': False, 'message': 'Invalid request format'},
            status=400
        )
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': str(e)},
            status=500
        )