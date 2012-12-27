# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q

from tools.models import Loaner

def handle_loan_messages(tools, loaner):
    tool_string = ''

    for tool in tools:
        if tool != tools[-1]:
            tool_string += tool + ', '
        else:
            tool_string += tool

    print tools
    print loaner
    print len(tools)

    message = loaner.name + ' har netop lånt værktøjet ' + tool_string

    if loaner.is_loan_flagged:
        admins = Loaner.objects.filter(Q(is_tool_admin=True)|
                                       Q(is_office_admin=True))
    else:
        admins = Loaner.objects.filter(sms_loan_threshold__lte=len(tools))

    for admin in admins:
        admin.send_sms(message)

    if loaner.is_loan_flagged:
        admins = Loaner.objects.filter(Q(is_tool_admin=True)|
                                       Q(is_office_admin=True))
    else:
        admins = Loaner.objects.filter(email_loan_threshold__lte=len(tools))

    for admin in admins:
        admin.send_mail('Værktøj udlånt', message)

