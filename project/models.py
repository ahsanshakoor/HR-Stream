import os

from django.db import models

from accounts.forms import User
from accounts.models import Company, CompanyClient
from django import template

from home.validator import MaxSizeValidator


def get_company_project_path(instance, filename):
    return 'company_{0}/{1}/{2}/{3}/{4}'.format(instance.company.id, 'files', 'project', instance.type, filename)


class Project(models.Model):
    START = 'start'
    FINISHED = 'finished'
    IN_PROGRESS = 'in_progress'
    PENDING = 'Pending'
    APPROVED = 'approved'
    ZERO = '0%'
    TEN = '10%'
    TWENTY = '20%'
    THIRTY = '30%'
    FOURTY = '40%'
    FIFTY = '50%'
    SIXTY = '60%'
    SEVENTY = '70%'
    EIGHTY = '80%'
    NINTY = '90%'
    HUNDRED = '100%'
    PROGRESS = (
        (ZERO, '0%'),
        (TEN, '10%'),
        (TWENTY, '20%'),
        (THIRTY, '30%'),
        (FOURTY, '40%'),
        (FIFTY, '50%'),
        (SIXTY, '60%'),
        (SEVENTY, '70%'),
        (EIGHTY, '80%'),
        (NINTY, '90%'),
        (HUNDRED, '100%'),
    )
    STATUS = (
        (START, 'Start'),
        (FINISHED, 'Finished'),
        (IN_PROGRESS, 'In Progress'),
        (PENDING, 'Pending'),
    )
    High = 'High'
    Medium = 'Medium'
    Low = 'Low'
    PRIORITY = (
        (High, 'High'),
        (Medium, 'Medium'),
        (Low, 'Low'),
    )
    Fixed = 'Fixed'
    Hourly = 'Hourly'
    RATE = (
        (Fixed, 'Fixed'),
        (Hourly, 'Hourly')
    )
    name = models.CharField(max_length=100, verbose_name='Project')
    code = models.CharField(max_length=100, verbose_name='Project Code')
    description = models.TextField(verbose_name='Project Name')
    start_date = models.DateField(verbose_name='Project Start Date')
    end_date = models.DateField(verbose_name='Project End Date')
    Project_status = models.CharField(max_length=25, choices=STATUS, default=PENDING, null=True, blank=True)
    Project_state = models.BooleanField(default=False, verbose_name='Project State')
    priority = models.CharField(max_length=25, choices=PRIORITY, default=High, null=True, blank=True)
    progress = models.CharField(max_length=25, choices=PROGRESS, default=ZERO, null=True, blank=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Rate', null=True, blank=True)
    rate_type = models.CharField(max_length=25, choices=RATE, default=Hourly, null=True, blank=True)
    estimated_time = models.PositiveIntegerField(verbose_name='Estimated Time', null=True, blank=True)
    lead_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Project Lead By',
                                related_name='user_project_lead')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company',
                                related_name='company_project')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Project Created By',
                                   related_name='user_project')
    # client = models.ForeignKey(CompanyClient, on_delete=models.CASCADE, verbose_name='Project Client',
    #                                related_name='user_project_client', null=True, blank=True,)
    client = models.ManyToManyField(CompanyClient, verbose_name='Project Client',
                                    related_name='project_clients', blank=True)
    team = models.ManyToManyField(User, verbose_name='Project Team',
                                  related_name='user_project_team')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class ProjectFile(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Uploaded By',
                                    related_name='user_files', null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Project Name',
                                related_name='project_files')
    file = models.FileField(upload_to=get_company_project_path, verbose_name='File', validators=[MaxSizeValidator(5)], max_length=1000)
    type = models.CharField(max_length=25, verbose_name='File Type', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company',
                                related_name='projectFileCompany', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def filename(self):
        return os.path.basename(self.file.name)

#
# class Team(models.Model):
#     name = models.CharField(max_length=100, verbose_name='Team Name', null=True)
#     lead_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Team Lead By',
#                                 related_name='user_team_lead')
#     member = models.ManyToManyField(User, verbose_name='Team Members',
#                                   related_name='user_team_member')
