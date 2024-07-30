from django.core.management.base import BaseCommand
from secret_santa.bot import Command as BotCommand

class Command(BaseCommand):
    help = 'Runs the bot'

    def handle(self, *args, **options):
        BotCommand().handle(*args, **options)