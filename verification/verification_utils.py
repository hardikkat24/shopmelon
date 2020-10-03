from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from verification.verification_tokens import account_activation_token
from django.core.mail import EmailMessage


def send_cofirmation_mail(user, site):
    subject = 'Activate your shopmelon account'
    message = render_to_string('verification/verification_mail.html', {
        'user': user,
        'domain': site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user)
    })
    email_id = user.email
    email = EmailMessage(subject, message, to = [email_id])
    email.send()
    print('sent')
    return