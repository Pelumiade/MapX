import smtplib

from django.conf import settings
from django.core.mail import EmailMessage

def send_email(data):
    try:
        email = EmailMessage(
            subject=data['email_subject'],
            body=data['email_body'],
            from_email=settings.EMAIL_HOST_USER,
            to=[data['to_email']]
        )
        email.send(fail_silently=False)
    except smtplib.SMTPException as e:
        print(f"An error occured: {e}")

    print("sent")