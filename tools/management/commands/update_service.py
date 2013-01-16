# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

from toolcontrol.utils import check_for_service

from tools.models import Employee, Tool

class Command(BaseCommand):
    help = 'Sends a mail to every employee that has a tool that needs service'

    def handle(self,*args, **options):
        # First, message the admins of the tools that need service
        tools = Tool.objects.all()
        tools_to_service = []

        for tool in tools:
            if check_for_service(tool):
                tools_to_service.append(tool)
        
        message = 'Daglig serviceopdatering. Følgende værktøj mangler service:\n'
        
        if not tools_to_service:
            message += 'Intet!'
        else:
            for tool in tools_to_service:
                message += '%s (%s)\n'% (tool.name, tool.get_location())

        for admin in Employee.objects.filter(is_tool_admin=True):
            admin.send_sms(message)

        # Send SMS to all loaners who have tools that need service
        for employee in Employee.objects.filter(is_employee=True):
            tools_to_service = []
        
            for tool in employee.tool_set.all():
                if check_for_service(tool):
                    tools_to_service.append(tool)

            message = 'Daglig serviceopdatering. Følgende værktøj i din besiddelse mangler service:\n'

            for tool in tools_to_service:
                message += '%s\n' % tool.name

            if tools_to_service:
                employee.send_sms(message)
