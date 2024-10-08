import datetime

from django.db import models

# from accounts.models import Company
from accounts.models import User


class LeavePolicy(models.Model):
    Monday = 'Monday'
    Tuesday = 'Tuesday'
    Wednesday = 'Wednesday'
    Thursday = 'Thursday'
    Friday = 'Friday'
    Saturday = 'Saturday'
    Sunday = 'Sunday'

    DAYS_OF_WEEK = (
        (Monday, 'Monday'),
        (Tuesday, 'Tuesday'),
        (Wednesday, 'Wednesday'),
        (Thursday, 'Thursday'),
        (Friday, 'Friday'),
        (Saturday, 'Saturday'),
        (Sunday, 'Sunday'),
    )
    YEARLY = 'Yearly'
    MONTHLY = 'Monthly'
    TWICE_A_MONTH = 'Twice amonth'
    WEEKLY = 'Weekly'
    CYCLE = (
        (YEARLY, 'Yearly'),
        (MONTHLY, 'Monthly'),
        (TWICE_A_MONTH, 'Twice amonth'),
        (WEEKLY, 'Weekly')
    )
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, null=True, blank=True, related_name='leavePolicyCompany')
    name = models.CharField(max_length=25, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cycle_type = models.CharField(max_length=15, choices=CYCLE, null=True, blank=True)
    cycle_start_date = models.DateField(verbose_name='Cycle Start Date', default=datetime.date.today)
    cycle_end_date = models.DateField(verbose_name='Cycle End Date', default=datetime.date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class Holiday(models.Model):

    leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, null=True, blank=True, related_name='holidayCompany')
    name = models.CharField(max_length=25, null=True, blank=True)
    date = models.DateField(verbose_name='Date', )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class Leave(models.Model):

    leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, null=True, blank=True, related_name='leaves')
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, null=True, blank=True, related_name='leaveTypeCompany')
    name = models.CharField(max_length=25, null=True, blank=True)
    days = models.IntegerField(verbose_name='Leave Days')
    is_carry_forward = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class LeaveRequest(models.Model):
    New = 'New'
    Pending = 'Pending'
    Approved = 'Approved'
    Declined = 'Declined'
    Status = (
        (New, 'New'),
        (Pending, 'Pending'),
        (Approved, 'Approved'),
        (Declined, 'Declined')
    )
    leave_from = models.DateField(verbose_name='Leave Start Date')
    leave_to = models.DateField(verbose_name='Leave End Date')
    requested_days = models.IntegerField(verbose_name='Requestd days')
    reason = models.TextField(verbose_name='Reason For Leave')
    status = models.CharField(max_length=10, verbose_name='Status Of Leave request',choices=Status, default=New)
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employeeLeaveRequest')
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, null=True, blank=True, related_name='leaveRequestCompany')
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaveRequestApprover', null=True)
    leave_type = models.ForeignKey(Leave, on_delete=models.PROTECT, related_name='leaveLeaveRequest', null=True)
    updated_at = models.DateTimeField(auto_now=True)

# class LeaveStatus(models.Model):


class WorkingDay(models.Model):

    day = models.CharField(max_length=10, null=True, blank= True)

    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, null=True, blank=True, related_name='workingDayCompany')
    leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.day)


class LeaveStatistics(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employeeLeaveStatistics')
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE, null=True, blank=True, related_name='leaveStatisticsCompany')
    leave_type = models.ForeignKey(Leave, on_delete=models.PROTECT, related_name='leaveLeaveStatistics')
    remaining_days = models.IntegerField(verbose_name='Leave Remaining Days')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)