import os
from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import Signal, receiver
from django.template.loader import render_to_string


user_registered = Signal()
password_reset_requested = Signal()

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5500')


def send_email(subject, text, template, context, recipient):
    send_mail(
        subject,
        text,
        settings.DEFAULT_FROM_EMAIL,
        [recipient],
        html_message=render_to_string(template, context),
        fail_silently=False,
    )


@receiver(user_registered)
def send_activation_email(sender, user, token, **kwargs):
    link = f"http://127.0.0.1:5500/pages/auth/activate.html?uid={user.pk}&token={token}"

    send_email(
        'Activate Your Videoflix Account',
        f'Please activate your account by visiting: {link}',
        'activation_mail.html',
        {'user_name': user.email, 'activation_link': link},
        user.email,
    )


@receiver(password_reset_requested)
def send_password_reset_email(sender, user, token, **kwargs):
    link = f"http://127.0.0.1:5500/pages/auth/confirm_password.html?uid={user.pk}&token={token}"
    hours = getattr(settings, 'PASSWORD_RESET_TIMEOUT', 86400) // 3600

    send_email(
        'Reset Your Videoflix Password',
        f'Please reset your password by visiting: {link}',
        'password_reset_mail.html',
        {'user': user, 'reset_link': link, 'reset_link_valid_hours': hours},
        user.email,
    )