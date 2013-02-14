# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import datetime

from django.db.models import Q
from django.utils import timezone

from tools.models import Employee
from toolcontrol.enums import MESSAGES

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

verbose_messages = {
    MESSAGES.TOOL_SERVICE_SUCCESS: ' blev serviceret',
    MESSAGES.TOOL_SERVICE_LOAN: ' blev ikke serviceret (værktøj udlånt)',
    MESSAGES.TOOL_SERVICE_SCRAPPED: ' blev ikke serviceret (værktøj kasseret)',
    MESSAGES.TOOL_SERVICE_LOST: ' blev ikke serviceret (værktøj bortkommet)',
    MESSAGES.TOOL_SERVICE_REPAIR: 'blev ikke serviceret (værktøj til reparation',

    MESSAGES.TOOL_LOAN_SUCCESS: ' blev udlånt',
    MESSAGES.TOOL_LOAN_LOAN: ' blev ikke udlånt (værktøj allerede udlånt)',
    MESSAGES.TOOL_LOAN_SCRAPPED: ' blev ikke udlånt (værktøj kasseret)',
    MESSAGES.TOOL_LOAN_LOST: ' blev ikke udlånt (værktøj bortkommet)',
    MESSAGES.TOOL_LOAN_REPAIR: ' blev ikke udlånt (værktøj til reparation)',
    MESSAGES.TOOL_LOAN_RESERVED: ' blev ikke udlånt (værktøj reserveret)',

    MESSAGES.TOOL_RESERVE_SUCCESS: ' blev reserveret',
    MESSAGES.TOOL_RESERVE_RESERVED: ' blev ikke reserveret (allerede reserveret i perioden)',
    MESSAGES.TOOL_RESERVE_SCRAPPED: ' blev ikke reserveret (værktøj kasseret)',
    MESSAGES.TOOL_RESERVE_LOST: ' blev ikke reserveret (værktøj bortkommet)',

    MESSAGES.TOOL_REPAIR_SUCCESS: ' blev sendt til reparation',
    MESSAGES.TOOL_REPAIR_LOAN: ' blev ikke sendt til reparation (værktøj udlånt)',
    MESSAGES.TOOL_REPAIR_SCRAPPED: ' blev ikke sendt til reparation (værktøj kasseret)',
    MESSAGES.TOOL_REPAIR_LOST: ' blev ikke sendt til reparation (værktøj bortkommet)',
    MESSAGES.TOOL_REPAIR_REPAIR: ' blev ikke sendt til reparation (værktøj allerede til reparation)',

    MESSAGES.TOOL_RETURN_SUCCESS: ' blev afleveret',
    MESSAGES.TOOL_RETURN_LOST: ' blev ikke afleveret (værktøj kasseret)',
    MESSAGES.TOOL_RETURN_SCRAPPED: ' blev ikke afleveret (værktøj bortkommet)',
    MESSAGES.TOOL_RETURN_STORE: ' blev ikke afleveret (værktøj allerede på lageret)',

    MESSAGES.TOOL_SCRAP_SUCCESS: 23,
    MESSAGES.TOOL_SCRAP_LOAN: 24,
    MESSAGES.TOOL_SCRAP_SCRAPPED: 25,
    MESSAGES.TOOL_SCRAP_LOST: 26,
    MESSAGES.TOOL_SCRAP_REPAIR: 27,

    MESSAGES.TOOL_LOST_SUCCESS: 28,
    MESSAGES.TOOL_LOST_LOAN: 29,
    MESSAGES.TOOL_LOST_SCRAPPED: 30,
    MESSAGES.TOOL_LOST_LOST: 31,
    MESSAGES.TOOL_LOST_REPAIR: 32,

    MESSAGES.EMPLOYEE_MAKE_ACTIVE_SUCCESS: 33,
    MESSAGES.EMPLOYEE_MAKE_ACTIVE_ACTIVE: 34,

    MESSAGES.EMPLOYEE_MAKE_INACTIVE_SUCCESS: 35,
    MESSAGES.EMPLOYEE_MAKE_INACTIVE_INACTIVE: 36,

    MESSAGES.EMPLOYEE_MAKE_ADMIN_SUCCESS: 37,
    MESSAGES.EMPLOYEE_MAKE_ADMIN_ADMIN: 38,

    MESSAGES.EMPLOYEE_REMOVE_ADMIN_SUCCESS: 39,
    MESSAGES.EMPLOYEE_REMOVE_ADMIN_ADMIN: 40,

    MESSAGES.EMPLOYEE_SET_LOAN_FLAG_SUCCESS: 41,
    MESSAGES.EMPLOYEE_SET_LOAN_FLAG_FLAGGED: 42,

    MESSAGES.EMPLOYEE_REMOVE_LOAN_FLAG_SUCCESS: 43,
    MESSAGES.EMPLOYEE_REMOVE_LOAN_FLAG_FLAGGED: 44,

    MESSAGES.CONSTRUCTION_SITE_MAKE_ACTIVE_SUCCESS: 45,
    MESSAGES.CONSTRUCTION_SITE_MAKE_ACTIVE_ACTIVE: 46,

    MESSAGES.CONSTRUCTION_SITE_MAKE_INACTIVE_SUCCESS: 47,
    MESSAGES.CONSTRUCTION_SITE_MAKE_INACTIVE_INACTIVE: 48,

    MESSAGES.CONTAINER_LOAN_SUCCESS: 49,
    MESSAGES.CONTAINER_LOAN_LOAN: 50,

    MESSAGES.CONTAINER_RETURN_SUCCESS: 51,
    MESSAGES.CONTAINER_RETURN_LOAN: 52,

    MESSAGES.CONTAINER_MAKE_ACTIVE_SUCCESS: 53,
    MESSAGES.CONTAINER_MAKE_ACTIVE_ACTIVE: 54,

    MESSAGES.CONTAINER_MAKE_INACTIVE_SUCCESS: 55,
    MESSAGES.CONTAINER_MAKE_INACTIVE_INACTIVE: 56,
}

def make_message(obj_dict):
    message = ''

    for i, key in enumerate(obj_dict,start=1):
        message += pretty_concatenate(obj_dict[key])
        message += verbose_messages[key]

        if i != len(obj_dict):
            message += "<br>"

    return message

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
