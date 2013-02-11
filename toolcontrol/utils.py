# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db.models import Q
from django.utils import timezone

from tools.models import Employee

def handle_loan_messages(tools, loaner):
    tool_string = ''

    for tool in tools:
        if tool != tools[-1]:
            tool_string += tool + ', '
        else:
            tool_string += tool

    message = loaner.name + ' har netop lånt værktøjet ' + tool_string

    if loaner.is_loan_flagged:
        admins = Employee.objects.filter(Q(is_tool_admin=True)|
                                       Q(is_office_admin=True))
    else:
        admins = Employee.objects.filter(sms_loan_threshold__lte=len(tools))

    for admin in admins:
        admin.send_sms(message)

    if loaner.is_loan_flagged:
        admins = Employee.objects.filter(Q(is_tool_admin=True)|
                                       Q(is_office_admin=True))
    else:
        admins = Employee.objects.filter(email_loan_threshold__lte=len(tools))

    for admin in admins:
        admin.send_mail('Værktøj udlånt', message)

def check_for_service(tool):
    if tool.service_interval == 0:
        return False

    now = timezone.now()
    service_interval = datetime.timedelta(days=tool.service_interval*30*0.9)

    # Find out whether the time between last service and now is bigger than
    # the max service interval
    return now - tool.last_service > service_interval

def pretty_concatenate(names):
    string = ''

    for name in names:
        if name == names[0]:
            string = name
        elif name == names[-1]:
            string += ' og ' + name
        else:
            string += ', ' + name

    return string
