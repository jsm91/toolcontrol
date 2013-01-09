# -*- coding:utf-8 -*-
from tools.models import Loaner
from django_cron import cronScheduler, Job

class CheckForService(Job):
    run_every = 60

    def job(self):
        loaner = Loaner.objects.get(id=1)
        loaner.send_email("Hej", "Nu er der gået et minut")

cronScheduler.register(CheckForService)
