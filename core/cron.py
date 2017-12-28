from django_cron import CronJobBase, Schedule
from django.conf import settings
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token

from datetime import datetime, timedelta




class RefreshTokenCron(CronJobBase):
    """
    class of cron for refresh Tokens. read doc django_cron
    """
    RUN_EVERY_MINS = 10  # start every 1 minutes

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.refresh_token_cron'

    def do(self):
        delta_dt = datetime.now() - timedelta(days=7) # refresh older that 7 days
        tokens = Token.objects.filter(created__lte=delta_dt)[:100]
        for token in tokens:
            user = token.user_id
            token.delete()
            Token.objects.get_or_create(user_id=user)
