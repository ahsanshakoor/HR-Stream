from django.core.validators import MinValueValidator
from django.db import models


from accounts.models import User


class Task(models.Model):
    START = 'start'
    FINISHED = 'finished'
    IN_PROGRESS = 'in_progress'
    REJECTED = 'rejected'
    APPROVED = 'approved'
    STATUS = (
        (START, 'Start'),
        (FINISHED, 'Finished'),
        (IN_PROGRESS, 'In Progress'),
        (REJECTED, 'Rejected'),
        (APPROVED, 'Approved'),
    )
    title = models.CharField(max_length=125)
    description = models.TextField(max_length=255, null=True, blank=True)
    priority = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    assign_to = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(upload_to='task_files/', null=True, blank=True, max_length=1000)
    due_date = models.DateTimeField(verbose_name='Due Date')
    status = models.CharField(max_length=25, choices=STATUS, default=START, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)
