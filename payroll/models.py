import os

from django.db import models
from django.utils import timezone

from accounts.models import User, Company


def get_company_claims_path(instance, filename):
    return 'company_{0}/{1}/{2}/{3}/{4}'.format(instance.company.id, 'files',  'claims', instance.type, filename)


class Payroll(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payroll')
    start_date = models.DateField(verbose_name='Date From')
    end_date = models.DateField(verbose_name='Date To')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='company_payroll', null=True, blank=True)

    gross_salary = models.DecimalField(max_digits=40, decimal_places=2, null=True, blank=True)
    net_salary = models.DecimalField(max_digits=40, decimal_places=2, null=True, blank=True)
    amount_401K = models.DecimalField(max_digits=40, decimal_places=2, null=True, blank=True)
    overtime = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    overtime_amount = models.DecimalField(max_digits=40, decimal_places=2, null=True, blank=True)
    working_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    leave_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    payroll_code = models.CharField(max_length=10, verbose_name='Payroll Code', null=True, blank=True)
    published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class PayrollTax(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_payroll_tax')
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='payroll_taxes')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_payroll_taxes')
    name = models.CharField(max_length=150, verbose_name='Payroll Item Name')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Tax Percentage')
    tax_amount = models.DecimalField(max_digits=40, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username}---{self.name}'


class PayrollPolicy(models.Model):
    YEARLY = 'yearly'
    MONTHLY = 'monthly'
    BI_MONTHLY = 'bi_monthly'
    BI_WEEKLY = 'bi_weekly'
    WEEKLY = 'weekly'
    CYCLE = (
        (WEEKLY, 'Weekly'),
        (BI_WEEKLY, 'Bi-Weekly'),
        (MONTHLY, 'Monthly'),
        (BI_MONTHLY, 'Bi-Monthly'),
        # (YEARLY, 'Yearly')
    )
    WEEKDAYS = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (0, 'Sunday')
    )
    DAYS = (
        (0, 'Sunday'), (1, '1st'), (2, '2nd'), (3, '3rd'), (4, '4th'), (5, '5th'), (6, '6th'), (7, '7th'), (8, '8th'),
        (9, '9th'), (10, '10th'), (11, '11th'), (12, '12th'), (13, '13th'), (14, '14th'), (15, '15th'), (16, '16th'),
        (17, '17th'), (18, '18th'), (19, '19th'), (20, '20th'), (21, '21th'), (22, '22th'), (23, '23th'), (24, '24th'),
        (25, '25th'), (26, '26th'), (27, '27th'), (28, '28th'), (29, '29th'), (30, '30th'), (31, '31th'),
        (32, 'LastDay'),
    )
    name = models.CharField(max_length=150, verbose_name='Payroll Policy Name')
    description = models.TextField(null=True, blank=True)
    pay_period_start = models.PositiveSmallIntegerField(choices=DAYS)
    pay_period_end = models.PositiveSmallIntegerField(choices=DAYS)
    pay_period_start_date = models.DateField(verbose_name='Pay Period Start Date')
    pay_period_end_date = models.DateField(verbose_name='Pay Period End Date')
    next_pay_period_start_date = models.DateField()
    next_pay_period_end_date = models.DateField()
    payroll_cycle = models.CharField(max_length=15, choices=CYCLE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='Company')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Attendance Policy Created By', related_name='User')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SalaryAdjustment(models.Model):
    Benefit = 'benefit'
    Deduction = 'deduction'
    CLAIM = 'claim'
    TYPE = (
        (Benefit, 'Benefit'),
        (Deduction, 'Deduction'),
        (CLAIM, 'Claim')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_salary_adjustments')
    payroll = models.ForeignKey(Payroll, on_delete=models.CASCADE, related_name='payroll_salary_adjustments',
                                null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_salary_adjustments',
                             null=True, blank=True)
    name = models.CharField(max_length=150, null=True, blank=True)
    amount = models.DecimalField(max_digits=40, decimal_places=2, null=True, blank=True)
    adjustment_type = models.CharField(max_length=25, choices=TYPE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PayrollItem(models.Model):

    Benefit = 'benefit'
    Deduction = 'deduction'
    OverTime = 'OverTime'
    STATUS = (
        (Benefit, 'Benefit'),
        (Deduction, 'Deduction'),
        (OverTime, 'OverTime')
    )
    payroll_policy = models.ForeignKey(PayrollPolicy, on_delete=models.CASCADE, related_name='payroll_item_policy', verbose_name='Payroll Policy Name')
    name = models.CharField(max_length=150, verbose_name='Payroll Item Name')
    amount = models.DecimalField(max_digits=40, decimal_places=2, verbose_name='Amount')
    adjustment_type = models.CharField(max_length=25, choices=STATUS, null=True, blank=True, verbose_name='Item Type')
    is_active = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='payrollItemCompany')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='payroll_item_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PayrollTaxItem(models.Model):
    payroll_policy = models.ForeignKey(PayrollPolicy, on_delete=models.CASCADE, related_name='payroll_tax_item_policy', verbose_name='Payroll Policy Name')
    name = models.CharField(max_length=150, verbose_name='Payroll Item Name')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Tax Percentage')
    is_active = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='payrollTaxItemCompany')
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='payroll_tax_item_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PendingPayrolls(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_pending_payrolls')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_pending_payrolls')
    start_date = models.DateField()
    end_date = models.DateField()
    working_hours_salary = models.DecimalField(max_digits=40, decimal_places=2, null=True, blank=True)
    benefit_amount = models.DecimalField(max_digits=40, decimal_places=2, null=True, blank=True)
    deduction_amount = models.DecimalField(max_digits=40, decimal_places=2, null=True, blank=True)
    taxes_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    overtime = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    working_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    leave_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()


class HealthInsurance(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_health_insurances')
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    company_amount = models.DecimalField(max_digits=40, decimal_places=2, default=0)
    employee_amount = models.DecimalField(max_digits=40, decimal_places=2, default=0)
    active = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='health_insurance_by_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ClaimType(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='claim_types')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Claim(models.Model):
    Pending = 'Pending'
    Approved = 'Approved'
    Declined = 'Declined'
    Status = (
        (Pending, 'Pending'),
        (Approved, 'Approved'),
        (Declined, 'Declined')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_claims', null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    claim_type = models.ForeignKey(ClaimType, on_delete=models.CASCADE, related_name='claims', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Amount', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_claims', null=True, blank=True)
    status = models.CharField(max_length=10, verbose_name='Status Of Claim', choices=Status, default=Pending)
    active = models.BooleanField(default=False)
    detail = models.TextField( null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


class ClaimFile(models.Model):
    file = models.FileField(upload_to=get_company_claims_path, verbose_name='File', null=True, blank=True, max_length=1000)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='claim_images_company', null=True, blank=True)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='claim_images', null=True, blank=True)
    type = models.CharField(max_length=25, verbose_name='File Type', null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def filename(self):
        return os.path.basename(self.file.name)