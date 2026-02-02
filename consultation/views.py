from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json

from .models import Consultation, ChatMessage, DoctorRating
from .forms import (
    ConsultationRequestForm,
    ChatMessageForm,
    DoctorRatingForm,
    ConsultationUpdateForm,
)
from accounts.models import DoctorProfile, PatientProfile
from prediction.models import PredictionHistory


@login_required
def doctor_list(request):
    """List all available doctors"""
    specialization = request.GET.get('specialization', '')

    if specialization:
        doctors = DoctorProfile.objects.filter(
            is_available=True,
            specialization__icontains=specialization
        )
    else:
        doctors = DoctorProfile.objects.filter(is_available=True)

    context = {
        'doctors': doctors,
    }
    return render(request, 'consultation/doctor_list.html', context)


@login_required
def consult_doctor(request, doctor_id):
    """Request consultation with a doctor"""
    if request.user.user_type != 'patient':
        messages.error(request, 'Only patients can request consultations.')
        return redirect('home')

    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    patient = getattr(request.user, 'patient_profile', None)
    if not patient:
        messages.error(request, 'Please complete your patient profile before requesting a consultation.')
        return redirect('accounts:edit_patient_profile', request.user.username)

    # Get latest prediction if exists
    latest_prediction = None
    try:
        latest_prediction = patient.predictions.latest('created_at')
    except PredictionHistory.DoesNotExist:
        pass

    if request.method == 'POST':
        form = ConsultationRequestForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.patient = patient
            consultation.doctor = doctor
            consultation.prediction = latest_prediction
            consultation.status = 'active'
            consultation.save()

            if latest_prediction:
                latest_prediction.consulted_doctor = True
                latest_prediction.save()

            messages.success(
                request,
                f'Consultation requested with Dr. {doctor.user.last_name}!'
            )
            return redirect(
                'consultation:consultation_view',
                consultation_id=consultation.id
            )
    else:
        initial_data = {}
        if latest_prediction:
            try:
                symptoms = json.loads(latest_prediction.symptoms) if latest_prediction.symptoms else []
            except Exception:
                symptoms = []
            predicted = getattr(latest_prediction, 'predicted_disease', None)
            disease_label = predicted.name if predicted else 'Unknown'
            initial_data['chief_complaint'] = (
                f"Predicted disease: {disease_label}\n"
                f"Symptoms: {', '.join(symptoms)}"
            )
        form = ConsultationRequestForm(initial=initial_data)

    context = {
        'form': form,
        'doctor': doctor,
    }
    return render(request, 'consultation/consultation.html', context)


@login_required
def consultation_view(request, consultation_id):
    """View consultation details and chat"""
    consultation = get_object_or_404(Consultation, id=consultation_id)

    # Parse symptoms JSON (stored as text on PredictionHistory) for easy display
    prediction_symptoms = []
    if consultation.prediction and consultation.prediction.symptoms:
        try:
            prediction_symptoms = json.loads(consultation.prediction.symptoms)
        except Exception:
            prediction_symptoms = []

    is_patient = request.user == consultation.patient.user
    is_doctor = request.user == consultation.doctor.user

    if not (is_patient or is_doctor):
        messages.error(request, 'You do not have permission to view this consultation.')
        return redirect('home')

    if request.method == 'POST':
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.consultation = consultation
            message.sender = request.user
            message.save()
            return redirect(
                'consultation:consultation_view',
                consultation_id=consultation_id
            )
    else:
        form = ChatMessageForm()

    if is_patient:
        consultation.messages.filter(
            sender=consultation.doctor.user, is_read=False
        ).update(is_read=True)
    elif is_doctor:
        consultation.messages.filter(
            sender=consultation.patient.user, is_read=False
        ).update(is_read=True)

    context = {
        'consultation': consultation,
        'messages': consultation.messages.all(),
        'form': form,
        'is_patient': is_patient,
        'is_doctor': is_doctor,
        'prediction_symptoms': prediction_symptoms,
        # patient can rate when they are the patient, consultation has no rating, and consultation is closed
        'can_rate': (
            is_patient and not hasattr(consultation, 'rating') and consultation.status == 'closed'
        ),
    }
    return render(request, 'consultation/consultation_view.html', context)


@login_required
def close_consultation(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)

    if request.user != consultation.doctor.user:
        messages.error(request, 'Only the doctor can close this consultation.')
        return redirect(
            'consultation:consultation_view',
            consultation_id=consultation_id
        )

    consultation.status = 'closed'
    consultation.closed_date = timezone.now()
    consultation.save()

    messages.success(request, 'Consultation closed successfully.')
    return redirect('consultation:consultation_history')


@login_required
def resume_consultation(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)

    if request.user != consultation.doctor.user:
        messages.error(request, 'Only the doctor can resume this consultation.')
        return redirect(
            'consultation:consultation_view',
            consultation_id=consultation_id
        )

    consultation.status = 'active'
    consultation.save()

    messages.success(request, 'Consultation resumed successfully.')
    return redirect(
        'consultation:consultation_view',
        consultation_id=consultation_id
    )


@login_required
def consultation_history(request):
    """
    Show consultation history for both patients and doctors.
    Uses Consultation model lookups instead of assuming profiles always exist,
    to avoid errors if a profile is missing.
    """
    if request.user.user_type == 'patient':
        consultations = Consultation.objects.filter(patient__user=request.user)
    elif request.user.user_type == 'doctor':
        consultations = Consultation.objects.filter(doctor__user=request.user)
    else:
        messages.error(request, 'Invalid user type.')
        return redirect('home')

    context = {
        'consultations': consultations,
    }
    return render(request, 'consultation/consultation_history.html', context)


@login_required
def rate_doctor(request, consultation_id):
    if request.user.user_type != 'patient':
        messages.error(request, 'Only patients can rate doctors.')
        return redirect('home')

    consultation = get_object_or_404(Consultation, id=consultation_id)

    if hasattr(consultation, 'rating'):
        messages.info(request, 'You have already rated this consultation.')
        return redirect(
            'consultation:consultation_view',
            consultation_id=consultation_id
        )

    patient_profile = getattr(request.user, 'patient_profile', None)
    if not patient_profile:
        messages.error(request, 'Please complete your patient profile before rating a doctor.')
        return redirect('accounts:edit_patient_profile', request.user.username)

    if request.method == 'POST':
        form = DoctorRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.patient = patient_profile
            rating.doctor = consultation.doctor
            rating.consultation = consultation
            rating.save()

            messages.success(request, 'Thank you for your feedback!')
            return redirect(
                'consultation:consultation_view',
                consultation_id=consultation_id
            )
    else:
        form = DoctorRatingForm()

    context = {
        'form': form,
        'consultation': consultation,
    }
    return render(request, 'consultation/rate_doctor.html', context)


@login_required
@require_POST
def send_message_ajax(request):
    try:
        data = json.loads(request.body)
        consultation_id = data.get('consultation_id')
        message_text = data.get('message')

        consultation = get_object_or_404(Consultation, id=consultation_id)

        is_patient = request.user == consultation.patient.user
        is_doctor = request.user == consultation.doctor.user

        if not (is_patient or is_doctor):
            return JsonResponse({'error': 'Access denied'}, status=403)

        message = ChatMessage.objects.create(
            consultation=consultation,
            sender=request.user,
            message=message_text
        )

        return JsonResponse({
            'id': message.id,
            'sender': message.sender.get_full_name(),
            'message': message.message,
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_messages_ajax(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)

    is_patient = request.user == consultation.patient.user
    is_doctor = request.user == consultation.doctor.user

    if not (is_patient or is_doctor):
        return JsonResponse({'error': 'Access denied'}, status=403)

    last_message_id = request.GET.get('last_id', 0)

    messages = consultation.messages.filter(id__gt=last_message_id).values(
        'id',
        'sender__first_name',
        'sender__last_name',
        'message',
        'created_at',
    )

    return JsonResponse({'messages': list(messages)})
