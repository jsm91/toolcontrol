import datetime

from django.template import Library
from django.utils import timezone

from tools.models import Tool

register = Library()

@register.filter
def check_for_service(value):
    if not isinstance(value,Tool):
        return False

    now = timezone.now()
    service_interval = datetime.timedelta(days=value.service_interval*30*0.9)

    return now > value.last_service + service_interval
