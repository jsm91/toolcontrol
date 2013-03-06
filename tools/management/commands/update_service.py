# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand

from toolcontrol.utils import check_for_service

from customers.models import Customer
from tools.models import Employee, Tool

class Command(BaseCommand):
    help = 'Sends a mail to every employee that has a tool that needs service'

    def handle(self,*args, **options):
        # First, message the admins of the tools that need service
        for customer in Customer.objects.all():
            tools = Tool.objects.filter(model__category__customer=customer)
            tools_to_service = []

            for tool in tools:
                if check_for_service(tool):
                    tools_to_service.append(tool)
        
            subject = 'Daglig serviceopdatering'
            message = 'Daglig serviceopdatering. Følgende værktøj mangler service:\n'
            
            if not tools_to_service:
                message += 'Intet!'
            else:
                for tool in tools_to_service:
                    message += '%s (%s)\n'% (tool.name, tool.get_location())

            for admin in Employee.objects.filter(customer=customer, is_admin=True):
                if admin.name != 'Henrik' and admin.name != 'Jacob Møller':
                    admin.send_message(subject, message)
                
        # Send SMS to all loaners who have tools that need service
        for employee in Employee.objects.all():
            tools_to_service = []
        
            for tool in employee.tool_set.all():
                if check_for_service(tool):
                    tools_to_service.append(tool)

            subject = 'Daglig serviceopdatering'
            message = 'Daglig serviceopdatering. Følgende værktøj i din besiddelse mangler service:\n'

            for tool in tools_to_service:
                message += '%s\n' % tool.name

            if (tools_to_service and employee.name != 'Henrik' and 
                employee.name != 'Jacob Møller'):
                employee.send_message(subject, message)



