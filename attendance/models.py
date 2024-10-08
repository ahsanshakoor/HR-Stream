from django.db import models
from multiselectfield import MultiSelectField

from accounts.models import User, Company


class Attendance(models.Model):
    employee = models.ForeignKey(User,on_delete=models.CASCADE, verbose_name='Employee', related_name='employeeAttendance' )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company',
                                related_name='employeeAttendanceCompany')
    date = models.DateField(verbose_name='Attendance Date')
    comment = models.TextField(verbose_name='Comment', null=True, blank=True)
    total_break = models.DecimalField(decimal_places=2, verbose_name='Total Break', max_digits=5,)
    total_duration = models.DecimalField(decimal_places=2, verbose_name='Total Duration', max_digits=5)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Attendance Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Attendance Updated At')


class AttendancePunch(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, verbose_name='Attendance', related_name='attendancePunch')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company',
                                related_name='attendancePunchCompany')

    in_time = models.TimeField(verbose_name='Punch In Time')
    out_time = models.TimeField(verbose_name='Punch Out Time', null=True, blank= True)
    duration = models.DecimalField(verbose_name='Punch duration', null=True, blank=True, max_digits=2, decimal_places=0)


# class AttendancePunchRequest(models.Model):
#
#     attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, verbose_name='Attendance',
#                                    related_name='attendancePunchRequests')
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company',
#                                 related_name='attendancePunchRequestCompany')
#     punch_time = models.TimeField(verbose_name='Punch Time')
#     punch_type = models.TextField(max_length=15)


class Shift(models.Model):

    Monday = 'Monday'
    Tuesday = 'Tuesday'
    Wednesday = 'Wednesday'
    Thursday = 'Thursday'
    Friday = 'Friday'
    Saturday = 'Saturday'
    Sunday = 'Sunday'
    DAYS_OF_WEEK = (
        (Monday , 'Monday'),
        (Tuesday, 'Tuesday'),
        (Wednesday, 'Wednesday'),
        (Thursday, 'Thursday'),
        (Friday, 'Friday'),
        (Saturday, 'Saturday'),
        (Sunday, 'Sunday'),
    )
    name = models.CharField(max_length=100, verbose_name='Shift Name')
    start_time = models.TimeField(verbose_name='Shift Start Time')
    end_time = models.TimeField(verbose_name='Shift End Time')
    weekdays = MultiSelectField(max_length=100, choices=DAYS_OF_WEEK, verbose_name='Weekend Days')
    shift_Allowance = models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Shift Allowance Amount', default=0)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company Name', related_name='shiftCompany')

    def __str__(self):
        return self.name


class AttendancePolicy(models.Model):
    Normal = 'Normal'
    Strict = 'Strict'
    Working_Hour_Policy = (
        (Normal, 'First Check-in & Last Check-out'),
        (Strict, 'Every Valid Check-in & Check-out ')
    )
    name = models.CharField(max_length=100, verbose_name='Attendance Policy Name')
    description = models.TextField(verbose_name='Attendance Policy Description')
    grace_time = models.DecimalField(verbose_name='Grace Time', max_digits=5, decimal_places=2)
    overtime = models.DecimalField(verbose_name='Overtime Allowed', max_digits=5, decimal_places=2)
    working_hour_policy = models.CharField(max_length=50, choices=Working_Hour_Policy, verbose_name='Working Hour Policy')
    # round_off = models.BooleanField(default=False)
    # punch_in = models.DecimalField(verbose_name='Punch In Round Off Time', null=True, blank=True, max_digits=5, decimal_places=2)
    # punch_out = models.DecimalField(verbose_name='Punch Out Round Off Time', null=True, blank=True, max_digits=5, decimal_places=2)
    working_hour = models.DecimalField(verbose_name='Total Working Hour Time Allowed', null=True, blank=True, max_digits=5, decimal_places=2)
    policy_status = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='attendancePolicyCompany')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Attendance Policy Created By', related_name='attendancePoilcyCreator')
    shift = models.ForeignKey(Shift, on_delete=models.PROTECT, null=True, blank=True, related_name='attendanceShift', verbose_name='Shift')

    def __str__(self):
        return self.name
