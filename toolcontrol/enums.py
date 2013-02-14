# -*- coding:utf-8 -*-
from __future__ import unicode_literals

class MESSAGES:
    TOOL_SERVICE_SUCCESS = 1
    TOOL_SERVICE_LOAN = 2
    TOOL_SERVICE_SCRAPPED = 3
    TOOL_SERVICE_LOST = 4
    TOOL_SERVICE_REPAIR = 5
    TOOL_SERVICE_RIGHTS = 60

    TOOL_LOAN_SUCCESS = 6
    TOOL_LOAN_LOAN = 7
    TOOL_LOAN_SCRAPPED = 8
    TOOL_LOAN_LOST = 9
    TOOL_LOAN_REPAIR = 10
    TOOL_LOAN_RESERVED = 11
    TOOL_LOAN_FAILURE = 59

    TOOL_RESERVE_SUCCESS = 12
    TOOL_RESERVE_RESERVED = 13
    TOOL_RESERVE_SCRAPPED = 14
    TOOL_RESERVE_LOST = 15

    TOOL_REPAIR_SUCCESS = 16
    TOOL_REPAIR_LOAN = 17
    TOOL_REPAIR_SCRAPPED = 18
    TOOL_REPAIR_LOST = 19
    TOOL_REPAIR_REPAIR = 20
    TOOL_REPAIR_RIGHTS = 62

    TOOL_RETURN_SUCCESS = 21
    TOOL_RETURN_STORE = 22
    TOOL_RETURN_SCRAPPED = 57
    TOOL_RETURN_LOST = 58
    TOOL_RETURN_RIGHTS = 63

    TOOL_SCRAP_SUCCESS = 23
    TOOL_SCRAP_LOAN = 24
    TOOL_SCRAP_SCRAPPED = 25
    TOOL_SCRAP_LOST = 26
    TOOL_SCRAP_REPAIR = 27
    TOOL_SCRAP_RIGHTS = 64

    TOOL_LOST_SUCCESS = 28
    TOOL_LOST_LOAN = 29
    TOOL_LOST_SCRAPPED = 30
    TOOL_LOST_LOST = 31
    TOOL_LOST_REPAIR = 32
    TOOL_LOST_RIGHTS = 65

    EMPLOYEE_MAKE_ACTIVE_SUCCESS = 33
    EMPLOYEE_MAKE_ACTIVE_ACTIVE = 34
    EMPLOYEE_MAKE_ACTIVE_RIGHTS = 66

    EMPLOYEE_MAKE_INACTIVE_SUCCESS = 35
    EMPLOYEE_MAKE_INACTIVE_INACTIVE = 36
    EMPLOYEE_MAKE_INACTIVE_RIGHTS = 67

    EMPLOYEE_MAKE_ADMIN_SUCCESS = 37
    EMPLOYEE_MAKE_ADMIN_ADMIN = 38
    EMPLOYEE_MAKE_ADMIN_RIGHTS = 68

    EMPLOYEE_REMOVE_ADMIN_SUCCESS = 39
    EMPLOYEE_REMOVE_ADMIN_ADMIN = 40
    EMPLOYEE_REMOVE_ADMIN_RIGHTS = 69

    EMPLOYEE_SET_LOAN_FLAG_SUCCESS = 41
    EMPLOYEE_SET_LOAN_FLAG_FLAGGED = 42
    EMPLOYEE_SET_LOAN_FLAG_RIGHTS = 70

    EMPLOYEE_REMOVE_LOAN_FLAG_SUCCESS = 43
    EMPLOYEE_REMOVE_LOAN_FLAG_FLAGGED = 44
    EMPLOYEE_REMOVE_LOAN_FLAG_RIGHTS = 80

    CONSTRUCTION_SITE_MAKE_ACTIVE_SUCCESS = 45
    CONSTRUCTION_SITE_MAKE_ACTIVE_ACTIVE = 46
    CONSTRUCTION_SITE_MAKE_ACTIVE_RIGHTS = 81

    CONSTRUCTION_SITE_MAKE_INACTIVE_SUCCESS = 47
    CONSTRUCTION_SITE_MAKE_INACTIVE_INACTIVE = 48
    CONSTRUCTION_SITE_MAKE_INACTIVE_RIGHTS = 82

    CONTAINER_LOAN_SUCCESS = 49
    CONTAINER_LOAN_LOAN = 50
    CONTAINER_LOAN_RIGHTS = 83

    CONTAINER_RETURN_SUCCESS = 51
    CONTAINER_RETURN_STORE = 52
    CONTAINER_RETURN_RIGHTS = 84

    CONTAINER_MAKE_ACTIVE_SUCCESS = 53
    CONTAINER_MAKE_ACTIVE_ACTIVE = 54
    CONTAINER_MAKE_ACTIVE_RIGHTS = 85

    CONTAINER_MAKE_INACTIVE_SUCCESS = 55
    CONTAINER_MAKE_INACTIVE_INACTIVE = 56
    CONTAINER_MAKE_INACTIVE_RIGHTS = 86

    OBJECT_DELETE_SUCCESS = 87
    OBJECT_DELETE_RIGHTS = 88

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
