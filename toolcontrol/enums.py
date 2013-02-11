# -*- coding:utf-8 -*-
from __future__ import unicode_literals

class TOOL_FAILURES:
    NOT_IN_STORE = 1
    NO_RIGHTS = 2
    NOT_ON_LOAN = 3
    UNKNOWN_ERROR = 4

verbose_action = {
    'delete': 'slettet',
    'service': 'serviceret',
    'end_loan': 'afleveret',
    'scrap': 'kasseret',
    'lost': 'markeret som bortkommet',
    'repair': 'repareret',
    'make_active': 'markeret som aktiv',
    'make_inactive': 'markeret som inaktiv',
    'make_tool_admin': 'markeret som værktøjsadmin',
    'make_not_tool_admin': 'markeret som ikke-værktøjsadmin',
    'make_office_admin': 'markeret som kontoradmin',
    'make_not_office_admin': 'markeret som ikke-kontoradmin',
    'make_loan_flagged': 'markeret med låneflag',
    'make_not_loan_flagged': 'markeret uden låneflag',
    'loan_single': 'udlånt',
}
