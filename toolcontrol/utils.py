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
    MESSAGES.TOOL_SERVICE_REPAIR: 'blev ikke serviceret (værktøj til reparation)',
    MESSAGES.TOOL_SERVICE_RIGHTS: 'blev ikke serviceret (du har ikke rettigheder til operationen)',

    MESSAGES.TOOL_LOAN_SUCCESS: ' blev udlånt',
    MESSAGES.TOOL_LOAN_LOAN: ' blev ikke udlånt (værktøj allerede udlånt)',
    MESSAGES.TOOL_LOAN_SCRAPPED: ' blev ikke udlånt (værktøj kasseret)',
    MESSAGES.TOOL_LOAN_LOST: ' blev ikke udlånt (værktøj bortkommet)',
    MESSAGES.TOOL_LOAN_REPAIR: ' blev ikke udlånt (værktøj til reparation)',
    MESSAGES.TOOL_LOAN_RESERVED: ' blev ikke udlånt (værktøj reserveret)',
    MESSAGES.TOOL_LOAN_FAILURE: ' blev ikke udlånt (intern fejl)',

    MESSAGES.TOOL_RESERVE_SUCCESS: ' blev reserveret',
    MESSAGES.TOOL_RESERVE_RESERVED: ' blev ikke reserveret (allerede reserveret i perioden)',
    MESSAGES.TOOL_RESERVE_SCRAPPED: ' blev ikke reserveret (værktøj kasseret)',
    MESSAGES.TOOL_RESERVE_LOST: ' blev ikke reserveret (værktøj bortkommet)',

    MESSAGES.TOOL_REPAIR_SUCCESS: ' blev sendt til reparation',
    MESSAGES.TOOL_REPAIR_LOAN: ' blev ikke sendt til reparation (værktøj udlånt)',
    MESSAGES.TOOL_REPAIR_SCRAPPED: ' blev ikke sendt til reparation (værktøj kasseret)',
    MESSAGES.TOOL_REPAIR_LOST: ' blev ikke sendt til reparation (værktøj bortkommet)',
    MESSAGES.TOOL_REPAIR_REPAIR: ' blev ikke sendt til reparation (værktøj allerede til reparation)',
    MESSAGES.TOOL_REPAIR_RIGHTS: ' blev ikke sendt til reparation (du har ikke rettigheder til operationen)',

    MESSAGES.TOOL_RETURN_SUCCESS: ' blev afleveret',
    MESSAGES.TOOL_RETURN_LOST: ' blev ikke afleveret (værktøj kasseret)',
    MESSAGES.TOOL_RETURN_SCRAPPED: ' blev ikke afleveret (værktøj bortkommet)',
    MESSAGES.TOOL_RETURN_STORE: ' blev ikke afleveret (værktøj allerede på lageret)',
    MESSAGES.TOOL_RETURN_RIGHTS: ' blev ikke afleveret (du har ikke rettigheder til operationen)',

    MESSAGES.TOOL_SCRAP_SUCCESS: ' blev kasseret',
    MESSAGES.TOOL_SCRAP_LOAN: ' blev ikke kasseret (værktøj udlånt)',
    MESSAGES.TOOL_SCRAP_SCRAPPED: ' blev ikke kasseret (værktøj allerede kasseret)',
    MESSAGES.TOOL_SCRAP_LOST: ' blev ikke kasseret (værktøj bortkommet)',
    MESSAGES.TOOL_SCRAP_REPAIR: ' blev ikke kasseret (værktøj til reparation)',
    MESSAGES.TOOL_SCRAP_RIGHTS: ' blev ikke kasseret (du har ikke rettigheder til operationen)',

    MESSAGES.TOOL_LOST_SUCCESS: ' blev markeret som bortkommet',
    MESSAGES.TOOL_LOST_LOAN: ' blev ikke markeret som bortkommet (værktøj udlånt)',
    MESSAGES.TOOL_LOST_SCRAPPED: ' blev ikke markeret som bortkommet (værktøj kasseret)',
    MESSAGES.TOOL_LOST_LOST: ' blev ikke markeret som bortkommet (værktøj allerede bortkommet)',
    MESSAGES.TOOL_LOST_REPAIR: ' blev ikke markeret som bortkommet (værktøj til reparation)',
    MESSAGES.TOOL_LOST_RIGHTS: ' blev ikke markeret som bortkommet (du har ikke rettigheder til operationen)',

    MESSAGES.EMPLOYEE_MAKE_ACTIVE_SUCCESS: ' blev markeret som aktiv',
    MESSAGES.EMPLOYEE_MAKE_ACTIVE_ACTIVE: ' blev ikke markeret som aktiv (allerede aktiv)',
    MESSAGES.EMPLOYEE_MAKE_ACTIVE_RIGHTS: ' blev ikke markeret som aktiv (du har ikke rettigheder til operationen)',

    MESSAGES.EMPLOYEE_MAKE_INACTIVE_SUCCESS: ' blev markeret som inaktiv',
    MESSAGES.EMPLOYEE_MAKE_INACTIVE_INACTIVE: ' blev ikke markeret som inaktiv (allerede inaktiv)',
    MESSAGES.EMPLOYEE_MAKE_INACTIVE_RIGHTS: ' blev ikke markeret som inaktiv (du har ikke rettigheder til operationen)',

    MESSAGES.EMPLOYEE_MAKE_ADMIN_SUCCESS: ' blev markeret som administrator',
    MESSAGES.EMPLOYEE_MAKE_ADMIN_ADMIN: ' blev ikke markeret som administrator (allerede administrator)',
    MESSAGES.EMPLOYEE_MAKE_ADMIN_RIGHTS: ' blev ikke markeret som administrator (du har ikke rettigheder til operationen)',

    MESSAGES.EMPLOYEE_REMOVE_ADMIN_SUCCESS: ' blev fjernet som administrator',
    MESSAGES.EMPLOYEE_REMOVE_ADMIN_ADMIN: ' blev ikke fjernet som administrator (allerede ikke administrator)',
    MESSAGES.EMPLOYEE_REMOVE_ADMIN_RIGHTS: ' blev ikke fjernet som administrator (du har ikke rettigheder til operationen)',

    MESSAGES.EMPLOYEE_SET_LOAN_FLAG_SUCCESS: ' blev markeret med låneflag',
    MESSAGES.EMPLOYEE_SET_LOAN_FLAG_FLAGGED: ' blev ikke markeret med låneflag (har allerede låneflag)',
    MESSAGES.EMPLOYEE_SET_LOAN_FLAG_RIGHTS: ' blev ikke markeret med låneflag (du har ikke rettigheder til operationen)',

    MESSAGES.EMPLOYEE_REMOVE_LOAN_FLAG_SUCCESS: ' fik fjernet låneflag',
    MESSAGES.EMPLOYEE_REMOVE_LOAN_FLAG_FLAGGED: ' fik ikke fjernet låneflag (havde ikke låneflag)',
    MESSAGES.EMPLOYEE_REMOVE_LOAN_FLAG_RIGHTS: ' fik ikke fjernet låneflag (du har ikke rettigheder til operationen)',

    MESSAGES.CONSTRUCTION_SITE_MAKE_ACTIVE_SUCCESS: ' blev markeret som aktiv',
    MESSAGES.CONSTRUCTION_SITE_MAKE_ACTIVE_ACTIVE: ' blev ikke markeret som aktiv (allerede aktiv)',
    MESSAGES.CONSTRUCTION_SITE_MAKE_ACTIVE_RIGHTS: ' blev ikke markeret som aktiv (du har ikke rettigheder til operationen)',

    MESSAGES.CONSTRUCTION_SITE_MAKE_INACTIVE_SUCCESS: ' blev markeret som inaktiv',
    MESSAGES.CONSTRUCTION_SITE_MAKE_INACTIVE_INACTIVE: ' blev ikke markeret som inaktiv (allerede inaktiv)',
    MESSAGES.CONSTRUCTION_SITE_MAKE_INACTIVE_RIGHTS: ' blev ikke markeret som inaktiv (du har ikke rettigheder til operationen)',

    MESSAGES.CONTAINER_LOAN_SUCCESS: ' blev udlånt',
    MESSAGES.CONTAINER_LOAN_LOAN: ' blev ikke udlånt (allerede udlånt)',
    MESSAGES.CONTAINER_LOAN_RIGHTS: ' blev ikke udlånt (du har ikke rettigheder til operationen)',

    MESSAGES.CONTAINER_RETURN_SUCCESS: ' blev afleveret',
    MESSAGES.CONTAINER_RETURN_STORE: ' blev ikke afleveret (allerede på lager)',
    MESSAGES.CONTAINER_RETURN_RIGHTS: ' blev ikke afleveret (du har ikke rettigheder til operationen)',

    MESSAGES.CONTAINER_MAKE_ACTIVE_SUCCESS: ' blev markeret som aktiv',
    MESSAGES.CONTAINER_MAKE_ACTIVE_ACTIVE: ' blev ikke markeret som aktiv (allerede aktiv)',
    MESSAGES.CONTAINER_MAKE_ACTIVE_RIGHTS: ' blev ikke markeret som aktiv (du har ikke rettigheder til operationen)',

    MESSAGES.CONTAINER_MAKE_INACTIVE_SUCCESS: ' blev markeret som inaktiv',
    MESSAGES.CONTAINER_MAKE_INACTIVE_INACTIVE: ' blev ikke markeret som inaktiv (allerede inaktiv)',
    MESSAGES.CONTAINER_MAKE_INACTIVE_RIGHTS: ' blev ikke markeret som inaktiv (du har ikke rettigheder til operationen)',

    MESSAGES.OBJECT_DELETE_SUCCESS: ' blev slettet',
    MESSAGES.OBJECT_DELETE_RIGHTS: ' blev ikke slettet (du har ikke rettigheder til operationen)',
}

def make_message(obj_dict):
    if len(obj_dict) == 0:
        return 'Ingen objekter valgt'

    if len(obj_dict) > 1:
        message = '<ul>'
    else:
        message = ''

    for key in obj_dict:
        if len(obj_dict) > 1:
            message += "<li>"

        message += pretty_concatenate(obj_dict[key])
        message += verbose_messages[key]

        if len(obj_dict) > 1:
            message += "</li>"

    if len(obj_dict) > 1:
        message += '</ul>'

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
