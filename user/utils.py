from django.template.loader import render_to_string
from django.core.mail import EmailMessage


def send_activation_confirmation_mail(user, site):
    subject = 'Shopmelon Verification Complete'
    message = render_to_string('user/activation_mail.html', {
        'user': user,
        'domain': site.domain,
    })
    email_id = user.email
    email = EmailMessage(subject, message, to = [email_id])
    email.send()
    return