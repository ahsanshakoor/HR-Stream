from django.utils import timezone
import pytz
from django import template


register = template.Library()


@register.filter(name='toLocalTime')
def toLocalTime(value):
    if value:
        tz = pytz.timezone(str(timezone.get_current_timezone()))
        now = timezone.now()
        n = now.replace(hour=value.hour, minute=value.minute, second=value.second, microsecond=value.microsecond)
        time = n.astimezone(tz).time()
        return time
