import datetime

from django.template import Library
from django.utils import timezone

from tools.models import Tool

register = Library()

@register.filter
def check_for_service(value):
    if not isinstance(value,Tool):
        return False

    if value.service_interval == 0:
        return False

    now = timezone.now()
    service_interval = datetime.timedelta(days=value.service_interval*30-7)

    # Find out whether the time between last service and now is bigger than
    # the max service interval
    return now - value.last_service > service_interval
