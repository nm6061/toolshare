import sendgrid
from django.conf import settings


def get_email_client():
    return sendgrid.SendGridClient(settings.SEND_GRID['username'], settings.SEND_GRID['password'])


def send_email(subject, message, to_addrs, from_addr=None, message_type='html'):
    msg = sendgrid.Mail()
    msg.add_to(to_addrs)
    msg.set_subject(subject)

    if message_type == 'html':
        msg.set_html(message)
    else:
        msg.set_text(message)

    if from_addr:
        msg.set_from(from_addr)
    else:
        msg.set_from(settings.DEFAULT_FROM_EMAIL)

    sg_client = get_email_client()
    status, msg = sg_client.send(msg)

    return status
