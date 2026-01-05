from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.staticfiles.storage import staticfiles_storage


def _send_email(user_email, user_name, subject, template_name, text_message, link_key, link_value):

    context = {
        'user_name': user_name,
        link_key: link_value,
        'STATIC_URL': staticfiles_storage.url(''),
    }

    html_content = render_to_string(template_name, context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email="noreply@videoflix.vincentgoerner.com",
        to=[user_email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()


def send_welcome_email(user_email, user_name, activation_link):

    text_content = (
        f"Hello {user_name},\n\n"
        f"Please activate your account here: {activation_link}"
    )

    _send_email(
        user_email=user_email,
        user_name=user_name,
        subject="Activate Your Videoflix Account",
        template_name="emails/welcome_email.html",
        text_message=text_content,
        link_key="activation_link",
        link_value=activation_link,
    )


def send_password_reset_email(user_email, user_name, reset_link):
    
    text_content = (
        f"Hello {user_name},\n\n"
        f"You can reset your password here: {reset_link}"
    )

    _send_email(
        user_email=user_email,
        user_name=user_name,
        subject="Reset Your Videoflix Password",
        template_name="emails/reset_password_email.html",
        text_message=text_content,
        link_key="reset_link",
        link_value=reset_link,
    )