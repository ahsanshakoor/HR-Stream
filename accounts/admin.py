from django.contrib import admin
from django.contrib.auth.models import Group
# Register your models here.
from accounts.models import User, Company, Role, RolePermission


class UserTable(admin.ModelAdmin):
    list_display = ('username', 'company', 'is_active')
    list_filter = ('role',)
    exclude = ('password', 'role', 'report_to' , 'department', 'designation', 'profile_pic', 'user_code', 'cell',
               'gender', 'user_type', 'joining_date', 'dob', 'address', 'on_boarding','percentage_401k',
               'apply_401k_before_tax', 'leave_policy', 'payroll_policy', 'attendance_policy', 'health_insurance',
               'created', 'updated', 'is_staff', 'date_joined', 'last_login', 'groups', 'is_superuser',
               'user_permissions')


class CompanyTable(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(User, UserTable)
admin.site.register(Company, CompanyTable)
admin.site.unregister(Group)
admin.site.site_header = "WorkDayStream Admin Panel"
admin.site.register(Role)
admin.site.register(RolePermission)

