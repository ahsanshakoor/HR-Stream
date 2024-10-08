from django.db import models

from accounts.models import User


class CheckIn(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    checkin = models.DateTimeField(verbose_name='CHECK_IN', default=None, null=True, blank=True)
    checkout = models.DateTimeField(verbose_name='CHECK_OUT',  null=True, blank=True)
    is_active = models.BooleanField(default=False)
    hour = models.FloatField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

