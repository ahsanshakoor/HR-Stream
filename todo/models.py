from django.db import models

from accounts.models import User, Company


class Todo(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='todos')
    title = models.TextField('', max_length=2500)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
