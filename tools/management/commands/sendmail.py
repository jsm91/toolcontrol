from django.core.management.base import BaseCommand
from tools.models import Loaner

class Command(BaseCommand):
    help = 'Sends a mail to a user'

    def handle(self,*args, **options):
        loaner = Loaner.objects.get(name='Henrik')
        loaner.send_sms('Hej med dig')
