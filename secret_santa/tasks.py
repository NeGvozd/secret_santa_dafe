from celery import shared_task
from django.utils import timezone
from .models import MailList
from .bot import send_mail


@shared_task
def send_scheduled_mails():
    now = timezone.now()
    mail_list = MailList.objects.filter(scheduled_time__lte=now, scheduled_time__isnull=False)

    for mail in mail_list:
        send_mail(mail.members.all(), mail.message, mail.image)
        mail.scheduled_time = None
        mail.save()