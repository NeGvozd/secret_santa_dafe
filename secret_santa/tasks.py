from django.utils import timezone
from .models import MailList
import requests


# @shared_task
def send_scheduled_mails():
    ...


def send_to_telegram(telegram_id, message, image=None):
    ... 