from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings


def contact_view(request):
    """Simple contact page that sends messages to site support (console backend)."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        message = request.POST.get('message', '').strip()

        if not (name and email and message):
            messages.error(request, 'Please provide your name, email and a message.')
            return render(request, 'contact.html', {
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'message': message,
            })

        subject = f"Contact form: {name}"
        body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nAddress: {address}\n\nMessage:\n{message}"
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@medicate.local')
        recipient = ['support@medicate.local']

        try:
            send_mail(subject, body, from_email, recipient, fail_silently=False)
            messages.success(request, 'Your message has been sent. We will get back to you shortly.')
            return redirect('contact')
        except Exception as e:
            messages.error(request, f'Failed to send message: {e}')

    return render(request, 'contact.html')
