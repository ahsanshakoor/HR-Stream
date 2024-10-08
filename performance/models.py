from django.db import models

from accounts.forms import User
from accounts.models import Company


class Indicator(models.Model):
    name = models.CharField(max_length=500, null=True, blank=True)
    total_weightage = models.PositiveIntegerField(null=True, blank=True)
    status = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Created By',
                                    related_name='userIndicator', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_indicator')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Performance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Employee Name', related_name='user_performance', null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Performance Created By',
                                   related_name='performance_created_by', null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='userPerformanceCompany', null=True, blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return self.employee


class PerformanceIndicator(models.Model):
    obtained_weightage = models.PositiveIntegerField(null=True, blank=True)
    total_weightage = models.PositiveIntegerField(null=True, blank=True)
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE, verbose_name='Performance',
                                       related_name='performanceindicators', null=True, blank=True)
    indicator = models.CharField(max_length=501, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company',
                                related_name='performance_indicator_company', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)