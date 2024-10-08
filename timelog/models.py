from django.db import models
from accounts.models import User, Company
from project.models import Project
from task.models import Task
from tasks.models import Card


class ManualTaskName(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='Manual_task_name')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class TimeLog(models.Model):
    PENDING = 'PENDING'
    SAVED = 'SAVED'
    SUBMITTED = 'SUBMITTED'
    REJECTED = 'REJECTED'
    APPROVED = 'APPROVED'
    MEEATING ='MEEATING'
    RESEARCH ='RESEARCH'
    DOCUMENTATION = 'DOCUMENTATION'
    MANUAL_TASK = (
        (MEEATING, 'MEEATING'),
        (RESEARCH, 'RESEARCH'),
        (DOCUMENTATION, 'DOCUMENTATION')
    )
    STATUS = (
        (REJECTED, 'REJECTED'),
        (APPROVED, 'APPROVED'),
        (PENDING, 'PENDING'),
    )
    SUBMIT_STATUS = (
        (SAVED, 'SAVED'),
        (SUBMITTED, 'SUBMITTED')
    )
    name = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='projectTimeLog')
    task = models.ForeignKey(Card, on_delete=models.CASCADE,  null=True, blank=True, related_name='taskTimeLog')
    company = models.ForeignKey(Company, on_delete=models.CASCADE,  null=True, blank=True, related_name='companyTimeLog')
    start_time = models.TimeField(verbose_name='Start Time', null=True, blank=True)
    end_time = models.TimeField(verbose_name='End Time', null=True, blank=True)
    date = models.DateField(verbose_name='Date', null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS, default=PENDING, null=True, blank=True)
    manual_task = models.ForeignKey(ManualTaskName, on_delete=models.PROTECT, null=True, blank=True)
    submit_status = models.CharField(max_length=25, choices=SUBMIT_STATUS, default=SAVED, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return str(self.task.name)


