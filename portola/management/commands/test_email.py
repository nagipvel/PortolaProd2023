from django.core.management.base import BaseCommand, CommandError
from portola.models import *
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from portola.email import Notification
from portola.utils import decrypt, encrypt

class Command(BaseCommand):
    help = 'sends a single test message'

    def handle(self, *args, **options):
        note = Notification()
        profile = Profile.objects.get(pk=3)
        token, _ = Token.objects.get_or_create(user = profile.user)
        note.email_user(username=profile.user.username,
            MFR = True,
            template='account_create',
            magic_link =  settings.CLIENT_HOST + '/forgot_password/' + encrypt(token)
        )
