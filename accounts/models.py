import os
from os.path import join
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from home.validator import MaxSizeValidator
from .currency import currency_list


def get_company_logo_path(instance, filename):
    return 'company_{0}/{1}'.format(instance.id, filename)


def get_company_users_profile_pics_path(instance, filename):
    return 'company_{0}/{1}/{2}/{3}'.format(instance.company.id, 'users', 'profile_pics', filename)


def get_company_users_files_path(instance, filename):
    return 'company_{0}/{1}/{2}/{3}'.format(instance.company.id, 'users', 'files', filename)


def get_company_clients_profile_pics_path(instance, filename):
    return 'company_{0}/{1}/{2}/{3}'.format(instance.company.id, 'clients', 'profile_pics', filename)


class Company(models.Model):
    """Save Company Profile"""

    CORPORATION = 'corporation'
    LLC = 'LLC'
    NON_PROFIT = 'NON_PROFIT'
    ENTITY_CHOICES = (
        (CORPORATION, 'Corporation'),
        (LLC, 'LLC'),
        (NON_PROFIT, 'Non Profit')
    )

    name = models.CharField(max_length=100)
    company_type = models.CharField(max_length=20, choices=ENTITY_CHOICES, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    date_established = models.DateField(blank=True, null=True)
    tag_line = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to=get_company_logo_path, blank=True, null=True, validators=[MaxSizeValidator(5)])
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    fax = models.CharField(max_length=20, blank=True, null=True)

    country = models.CharField(max_length=30, blank=True, null=True)
    state = models.CharField(max_length=30, blank=True, null=True)
    city = models.CharField(max_length=30, blank=True, null=True)
    zip = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)

    facebook_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)

    currency_code = models.CharField(max_length=4, choices=currency_list, null=True, blank=True)
    currency_sym = models.CharField(max_length=8, null=True, blank=True)
    currency_dir = models.CharField(max_length=5, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('mycompany_detail', args=[str(self.id)])


class Role(models.Model):
    company = models.ManyToManyField(Company, related_name='company_roles')
    name = models.CharField(max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ManyToManyField(Role, related_name='role_permissions', blank=True)
    name = models.CharField(max_length=30)
    name_value = models.CharField(max_length=30, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Designation(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_designations', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    EMPLOYEE = 'employee'
    CLIENT = 'client'
    USER_TYPES = (
        (EMPLOYEE, 'Employee'),
        (CLIENT, 'Client')
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    role = models.ManyToManyField(Role, related_name='users', blank=True)
    report_to = models.ForeignKey('self', on_delete=models.PROTECT, related_name='subordinates',
                                  null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='employees', null=True,
                                   blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.PROTECT, related_name='user_ranks', null=True,
                                    blank=True)
    profile_pic = models.ImageField(upload_to=get_company_users_profile_pics_path, blank=True, null=True, validators=[MaxSizeValidator(5)])
    user_code = models.CharField(max_length=20, null=True, blank=True)
    cell = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=6, choices=[('male', 'Male'), ('female', 'Female')], default='male')
    user_type = models.CharField(max_length=8, choices=USER_TYPES, default='employee')
    joining_date = models.DateField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    on_boarding = models.BooleanField(default=False, null=True, blank=True)
    timezone = models.CharField(max_length=50, null=True, blank=True)
    percentage_401k = models.PositiveSmallIntegerField(default=0)
    apply_401k_before_tax = models.BooleanField(default=False, choices=((True, 'Yes'), (False, 'No')))

    leave_policy = models.ForeignKey('leave.LeavePolicy', on_delete=models.PROTECT, related_name='user_leave_policy',
                                     null=True, blank=True)
    payroll_policy = models.ForeignKey('payroll.PayrollPolicy', on_delete=models.PROTECT,
                                       related_name='user_payroll_policy',
                                       null=True, blank=True)
    attendance_policy = models.ForeignKey('attendance.AttendancePolicy', on_delete=models.PROTECT,
                                          related_name='user_attendance_policy', null=True, blank=True)
    health_insurance = models.ForeignKey('payroll.HealthInsurance', on_delete=models.PROTECT,
                                         related_name='user_health_insurance', null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_full_name()


class UserSalary(models.Model):
    HOURLY = 'hourly'
    MONTHLY = 'monthly'
    YEARLY = 'yearly'
    SALARY_TYPE = (
        (HOURLY, 'Hourly'),
        (MONTHLY, 'Monthly'),
        (YEARLY, 'Yearly')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='UserSalaries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salaries')
    salary = models.DecimalField(max_digits=20, decimal_places=0)
    salary_raise = models.DecimalField(max_digits=20, decimal_places=0, default=0)
    employment_type = models.CharField(max_length=30, choices=[
        ('fulltime', 'Full Time'),
        ('parttime', 'Part Time'),
        ('intern', 'Intern')
    ], default='fulltime')
    salary_type = models.CharField(max_length=30, choices=SALARY_TYPE, default=YEARLY)
    comments = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class PersonalInfo(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='PersonalInfos')
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class EmergencyContact(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='EmergencyContacts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_emergency_contact', blank=True,
                             null=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    relationship = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=18, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class EducationInfo(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='EducationInfos')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_edu_info', blank=True,
                             null=True)
    institution = models.CharField(max_length=100, null=True, blank=True)
    degree = models.CharField(max_length=50, null=True, blank=True)
    starting_date = models.DateField(blank=True, null=True)
    ending_date = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class Experience(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='Experiences')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_experience', blank=True,
                             null=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    job_position = models.CharField(max_length=50, null=True, blank=True)
    period_from = models.DateField(blank=True, null=True)
    period_to = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class BankInfo(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='BankInfos')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_bank', blank=True,
                             null=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    routing = models.CharField(max_length=20, null=True, blank=True)
    account_no = models.CharField(max_length=30, null=True, blank=True)
    account_type = models.CharField(max_length=30, null=True, blank=True)
    account_title = models.CharField(max_length=50, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class CompanyClient(models.Model):
    user = models.ForeignKey('accounts.user', on_delete=models.CASCADE, related_name='user', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='clients')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='clients_created_by')

    stakeholder_name = models.CharField(max_length=150)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    profile_pic = models.ImageField(upload_to=get_company_clients_profile_pics_path, blank=True, null=True, validators=[MaxSizeValidator(5)])
    client_code = models.CharField(max_length=20, null=True, blank=True)
    cell = models.CharField(max_length=20, null=True, blank=True)
    # gender = models.CharField(max_length=6, choices=[('male', 'Male'), ('female', 'Female')], default='male')
    address = models.CharField(max_length=250, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{0} {1} ({2})'.format(self.first_name, self.last_name, self.stakeholder_name)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()


class UserFile(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='UserFiles')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userfiles')
    name = models.CharField(max_length=250)
    file = models.FileField(upload_to=get_company_users_files_path, validators=[MaxSizeValidator(5)], max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        self.file.delete()
        super().delete(using, keep_parents)

    def save(self, *args, **kwargs):
        try:
            # is the object in the database yet?
            obj = UserFile.objects.get(id=self.id)
        except UserFile.DoesNotExist:
            # object is not in db, nothing to worry about
            return super().save(*args, **kwargs)
            # is the save due to an update of the actual image file?
        if obj.file and self.file and obj.file != self.file:
            # delete the old image file from the storage in favor of the new file
            obj.file.delete()
        return super().save(*args, **kwargs)

    def filename(self):
        return os.path.basename(self.file.name)

class Announcement(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='announcements')
    announced_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title
