# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.management.base import BaseCommand

from toolcontrol.utils import check_for_service
from tools.models import Employee, Tool

class Command(BaseCommand):
    help = 'Sends an SMS to every employee that has a tool that is reserved'

    def handle(self,*args, **options):
        # Send SMS to all employees who have tools that are reserved
        for employee in Employee.objects.all():
            tools_to_return = []
        
            for tool in employee.tool_set.all():
                now = datetime.datetime.now()
                future = now + datetime.timedelta(days=3)
                if tool.is_reserved(now,future):
                    tools_to_return.append(tool)

            message = 'Daglig reservationsopdatering. Følgende værktøj i din besiddelse er reserveret inden for tre dage:\n'

            for tool in tools_to_return:
                now = datetime.datetime.now()
                future = now + datetime.timedelta(days=3)
                reservation = tool.is_reserved(now,future)[0]
                if reservation.employee != employee:
                    message += '%s (reserveret til %s fra %s)\n' % (tool.name, reservation.employee, reservation.start_date.isoformat())

            if tools_to_return:
                employee.send_sms(message)
