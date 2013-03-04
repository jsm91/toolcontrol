# -*- coding:utf-8 -*-
import logging
import traceback

from django.http import Http404
from django.shortcuts import get_object_or_404

from tools.models import Ticket

class DBLogHandler(logging.Handler):
    def emit(self, record):
        if record.exc_info:
            stack_trace = '\n'.join(traceback.format_exception(*record.exc_info))
        else:
            stack_trace = 'Ingen stack trace tilgængelig'

        try:
            org_ticket = get_object_or_404(Ticket, name=record.getMessage(),
                                           description=stack_trace,
                                           duplicate=None)
            
            t = Ticket(name=record.getMessage(), description=stack_trace, 
                       level='Fejl', duplicate=org_ticket)
        except Http404:
            t = Ticket(name=record.getMessage(), description=stack_trace, 
                       level='Fejl')
            
        t.save()
