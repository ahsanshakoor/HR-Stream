import datetime
import smtplib

import pytz
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.db.models import ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.html import format_html
from django.views import generic
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views import View
from django.views.generic.edit import FormMixin
from django.contrib.auth.hashers import make_password

from accounts.currency import currency_sym, currency_dir
from accounts.decorators import require_user_access_rights
from accounts.forms import SignupForm, NewEmployeeForm, NewEmployeeOnBoardingForm, DesignationForm, UserSalaryForm, \
    PersonalInfoForm, ProfileInfoForm, EmergencyContactForm, EducationInfoFormSet, ExperienceFormSet, BankInfoForm, \
    NewClientForm, DepartmentForm, UserFileFormSet, ProfileInfoFormWithoutRole, ClientEditForm, NewAnnouncementForm, \
    NewEmployeeSalaryForm, CurrencyForm
from accounts.mixins import CompanyRequiredMixin
from accounts.models import (User, Role, RolePermission,
                             Company, UserSalary, PersonalInfo, Department, Designation, EmergencyContact,
                             EducationInfo, Experience, BankInfo, CompanyClient, UserFile, Announcement)
from accounts.utils import get_company_object_from_user, user_has_access, get_object_or_404_template_default

from attendance.models import AttendancePolicy, Shift
from home.views import baseelements
from django.core import serializers

from leave.models import LeavePolicy
from payroll.models import PayrollPolicy
from project.models import Project


def send_confirmation_mail(request, user, renderTemplate, mail_subject, to_email):
    current_site = get_current_site(request)
    try:
        message = render_to_string(renderTemplate, {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        email = EmailMultiAlternatives(subject=mail_subject, body=message, to=[to_email])
        msg = EmailMultiAlternatives(
            # title:
            "Workday Stream Registration",
            # message:
            message,
            # from:
            'abdurrehman.ai78@gmail.com',
            # to:
            [to_email]
        )
        msg.attach_alternative(message, "text/html")

        msg.send()
    except smtplib.SMTPException as e:
        print(e)
        return False
    except Exception as e:
        print(e)
        return False
    return True


def send_confirmation_mail_to_client(request, client, user, password, renderTemplate, mail_subject, to_email):
    current_site = get_current_site(request)
    try:
        message = render_to_string(renderTemplate, {
            'user': user,
            'client': client,
            'password': password,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        email = EmailMultiAlternatives(subject=mail_subject, body=message, to=[to_email])
        msg = EmailMultiAlternatives(
            # title:
            "Workday Stream Registration",
            # message:
            message,
            # from:
            'admin@workdaystream.com',
            # to:
            [to_email]
        )
        msg.attach_alternative(message, "text/html")

        msg.send()
    except smtplib.SMTPException:
        return False
    except Exception as e:
        print(e)
        return False
    return True


# working
class SignUp(generic.CreateView):
    form_class = SignupForm
    template_name = 'registration/register.html'

    def post(self, request, *args, **kwargs):
        form = SignupForm(request.POST)
        # print(request.POST)
        if form.is_valid():
            print(form.changed_data)
            try:
                user = form.save(commit=False)
                user.is_active = False
                company = Company(name=form.cleaned_data['company_name'])
                company.save()
                user.company = company
                user.joining_date = timezone.now().date()
                user.save()
                pinfo = PersonalInfo(user=user, company=company)
                pinfo.save()

                try:
                    role = Role.objects.get(name='Owner')
                except:
                    messages.error(request, 'Please run create owner command first.')
                    return redirect('signup')

                user.role.add(role)
                salary = UserSalary(user=user, salary=0, salary_raise=0,
                                    employment_type='fulltime', salary_type='salary', company=company)
                salary.save()
            except:
                if Company.objects.filter(name=form.cleaned_data['company_name']).exists():
                    Company.objects.get(name=form.cleaned_data['company_name']).delete()
                messages.error(request, 'An error is occurred while processing your request. Please Try Again')
                return redirect('signup')

            mail_subject = ('Activate your {0} company  account'.format(form.cleaned_data['company_name']))
            return_value = send_confirmation_mail(request, user, 'registration/account_activation_by_email.html',
                                                  mail_subject, form.cleaned_data.get('email'))
            if return_value:
                messages.info(request, 'Please visit your inbox to confirm your email address')
                return redirect('login')
            else:
                company.delete()
                messages.error(request, 'An error is occurred while processing your email id. Please Try Again')

        return render(request, self.template_name, {'form': form})


# working
def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.on_boarding = True
        user.user_code = 'EMP-0001'
        user.save()
        messages.success(request, 'Congratulation. You are registered now. Please login')
        return redirect('login')
    else:
        messages.warning(request, 'Activation link is invalid. Try again.')
        return redirect('signup')


@require_POST
def check_username(request, uidb64, token):
    if request.is_ajax and request.method == 'POST':
        # print(request.POST)
        username = request.POST['username']
        if User.objects.filter(username=username).exists():
            # print('already')
            return JsonResponse({'available': True}, status=200)
        else:
            # print('available')
            return JsonResponse({'available': False}, status=200)
    return JsonResponse({'error': ''}, status=400)


# working
@require_user_access_rights(['owner', 'roles'])
@login_required
def create_n_edit_role(request, role_id=None):
    company = get_company_object_from_user(request.user.id)
    if request.method == "POST":
        role_name = request.POST['role_name'].strip()
        if role_name not in (None, ''):
            if role_id:
                role = get_object_or_404_template_default(Role, id=role_id, company=company)
                role.name = role_name
                role.save()
                messages.success(request, 'Role Name Update Successful!')
            else:
                if Role.objects.filter(company=company, name=role_name).exists():
                    messages.error(request, 'Role Name Already Exist.')
                else:
                    role = Role.objects.create(name=role_name)
                    role.company.add(company)
                    basic = RolePermission.objects.get(name_value='basic')
                    basic.role.add(role)
                    messages.success(request, 'Role Addition Successful!')
        else:
            messages.error(request, 'Role Name is Empty')
    return redirect('viewroles')


# working
@require_user_access_rights(['owner', 'roles'])
@login_required
def delete_role(request, role_id=None):
    company = get_company_object_from_user(request.user.id)
    if role_id is not None:
        role = get_object_or_404_template_default(Role, id=role_id, company=company)
        role.delete()
        messages.success(request, 'Role Deleted Successful!')
    return redirect('viewroles')


# working
@require_user_access_rights(['owner', 'roles'])
@login_required
def get_permissions_for_role(request, role_id=None):
    if request.is_ajax and request.method == 'GET':
        if role_id is not None:
            perms_checked = list(RolePermission.objects.filter(role=role_id).values_list('id', 'name_value', 'name'))
            perms = list(RolePermission.objects.exclude(name_value='owner').values_list('id', 'name_value', 'name'))
            return JsonResponse({'perms_checked': perms_checked, 'all_perms': perms}, status=200)
    return JsonResponse({'error': ''}, status=400)


# working
@require_user_access_rights(['owner', 'roles'])
@login_required
def update_role(request):
    company = get_company_object_from_user(request.user.id)
    if request.is_ajax and request.method == 'POST':
        roleID = request.POST['roleID']
        permissions_ids = request.POST.getlist('checkedIDs[]')

        role = get_object_or_404_template_default(Role.objects.prefetch_related('role_permissions'), id=roleID,
                                                  company=company)
        perms_objects = RolePermission.objects.filter(id__in=permissions_ids)
        role.role_permissions.clear()
        for obj in perms_objects:
            obj.role.add(role)
        return JsonResponse({'success': 'Role Update Successful!'}, status=200)
    return JsonResponse({'error': ''}, status=400)


# working
@require_user_access_rights(['owner', 'roles'])
@login_required
def view_role_permissions(request):
    company = get_company_object_from_user(request.user.id)
    roles_to_be_excluded = ['all_company_clients_role__', 'Owner']
    roles = Role.objects.filter(company=company).prefetch_related('role_permissions').exclude(name__in= roles_to_be_excluded)
    perms = RolePermission.objects.exclude(name_value='owner')
    context1 = {'roles': roles, 'perms': perms}
    return render(request, 'light/roles-permissions.html', context1)


# working
@require_user_access_rights(['owner', 'new_employees'])
@login_required
def view_company_employees(request):
    company = get_company_object_from_user(request.user.id)
    users = User.objects.filter(company=company, user_type=User.EMPLOYEE).exclude(role__name='Owner')
    return render(request, 'light/employees.html', {'users': users})


def is_it_allow_to_create_employee(request, company):
    if not company.logo:
        m = format_html('Please Update your <a href={} class="primary-color-used">Company Logo</a>',
                        reverse('mycompany_edit', args=[company.id]))
        messages.info(request, m)
        return False
    departments = Department.objects.filter(company=company).prefetch_related('designations').all()
    if departments.count() < 1:
        m = format_html('Please Add <a href={} class="primary-color-used">Departments</a> in your Company',
                        reverse('showDepartments'))
        messages.info(request, m)
        return False
    # print('Department => ' + str(departments.count()))
    designation_count = 0
    for dep in departments:
        designation_count += dep.designations.count()

    if designation_count < 1:
        m = format_html('Please Add <a href={} class="primary-color-used">Designations</a> in your Company',
                        reverse('showDesignations'))
        messages.info(request, m)
        return False
    # print('Designations => ' + str(designation_count))
    roles_count = Role.objects.filter(company=company).count()
    if roles_count < 1:
        m = format_html('Please Add <a href={} class="primary-color-used">Roles</a> in your Company',
                        reverse('viewroles'))
        messages.info(request, m)
        return False
    # print('Roles => ' + str(roles_count))

    payroll_count = PayrollPolicy.objects.filter(company=company).count()
    if payroll_count < 1:
        m = format_html('Please Add <a href={} class="primary-color-used">Payroll Policies</a> in your Company',
                        reverse('payroll_policies'))
        messages.info(request, m)
        return False
    # print('Payroll => ' + str(payroll_count))
    leave_policies = LeavePolicy.objects.filter(company=company).prefetch_related('leaves').all()
    if leave_policies.count() < 1:
        m = format_html('Please Add <a href={} class="primary-color-used">Leave Policies</a> in your Company',
                        reverse('leavepolicies'))
        messages.info(request, m)
        return False
    # print('Leave Policies => ' + str(leave_policies.count()))
    leave_type_count = 0
    for lp in leave_policies:
        leave_type_count += lp.leaves.count()

    if leave_type_count < 1:
        m = format_html('Please Add <a href={} class="primary-color-used">Leave Types</a> in your Company',
                        reverse('get_leave_type', args=[leave_policies.first().id]))
        messages.info(request, m)
        return False
    # print('Leave Types => ' + str(leave_type_count))

    attdnc_policies_count = AttendancePolicy.objects.filter(company=company).count()
    if attdnc_policies_count < 1:
        m = format_html('Please Add <a href={} class="primary-color-used">Attendance Policies</a> in your Company',
                        reverse('attendance_policies'))
        messages.info(request, m)
        return False
    # print('Attendance Policies => ' + str(attdnc_policies_count))
    shift_count = Shift.objects.filter(company=company).count()
    if shift_count < 1:
        m = format_html('Please Add <a href={} class="primary-color-used">Shifts</a> in your Company',
                        reverse('shift'))
        messages.info(request, m)
        return False
    # print('Shifts => ' + str(shift_count))
    return True


def get_employee_custom_id(request):
    pUser = User.objects.filter(company=get_company_object_from_user(request.user.id), user_type=User.EMPLOYEE).last()
    # print('user.......')
    # print(pUser)
    if pUser is None:
        user_code = 'EMP-0001'
    else:
        user_code = pUser.user_code
        if user_code in ('', None):
            user_code = 'EMP-0001'
            pUser.user_code = user_code
            pUser.save()
        # print(user_code)
        user_code_str = user_code[4:]
        user_code = 'EMP-{0:04d}'.format(int(user_code_str) + 1)
    return user_code


def get_client_custom_id(request):
    pClient = CompanyClient.objects.filter(company=get_company_object_from_user(request.user.id)).last()
    if pClient is None:
        client_code = 'CLI-0001'
    else:
        client_code = pClient.client_code
        # print(client_code)
        client_code_str = client_code[4:]
        client_code = 'CLI-{0:04d}'.format(int(client_code_str) + 1)
    return client_code


@require_user_access_rights(['owner', 'new_employees'])
@login_required
def create_company_employee(request):
    company = get_company_object_from_user(request.user.id)
    if not is_it_allow_to_create_employee(request, company):
        return redirect('view_employees')

    if request.method == 'POST':
        userForm = NewEmployeeForm(request.POST, company_name=company.name)
        userSalaryForm = NewEmployeeSalaryForm(request.POST)
        if userForm.is_valid() and userSalaryForm.is_valid():
            # print(userForm.cleaned_data)
            # print(userSalaryForm.cleaned_data)
            # return HttpResponse('okay')
            cd = userForm.cleaned_data
            user = userForm.save(commit=False)
            user.is_active = False
            user.company = company
            user.report_to = cd['report_to']
            user.save()
            for role in cd['role'].all():
                user.role.add(role)

            userSalary = userSalaryForm.save(commit=False)
            userSalary.user = user
            userSalary.company = company
            userSalary.save()

            mail_subject = ('Complete your on-boarding for {0} company  account'.format(company.name))
            return_value = send_confirmation_mail(request, user, 'registration/on_boarding_invitation_by_email.html',
                                                  mail_subject, userForm.cleaned_data.get('email'))
            if return_value:
                messages.info(request, 'Invite link has been sent')
                return redirect('view_employees')
            else:
                messages.error(request, 'An error is occurred while sending invite link. Please send Again')
        else:
            print('Unable to validate form')
    else:
        userForm = NewEmployeeForm(company_name=company.name, initial={'user_code': get_employee_custom_id(request)})
        userSalaryForm = NewEmployeeSalaryForm()
    return render(request, 'light/employee-new.html', {'userForm': userForm, 'userSalaryForm': userSalaryForm})


@require_user_access_rights(['owner', 'new_employees'])
@login_required
def resend_on_boarding_link(request, user_id=None):
    if request.is_ajax:
        company = get_company_object_from_user(request.user.id)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'This user does not exist. Please contact your admin'}, status=400)

        mail_subject = ('Complete your on-boarding for {0} company  account'.format(company.name))
        return_value = send_confirmation_mail(request, user, 'registration/on_boarding_invitation_by_email.html',
                                              mail_subject, user.email)
        if return_value:
            return JsonResponse({'success': 'Invite link has been sent'}, status=200)
        else:
            return JsonResponse({'error': 'An error is occurred while sending invite link. Please send Again'},
                                status=400)


def verify_on_boarding_token(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64)
    try:
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        company = get_company_object_from_user(uid)
        form = NewEmployeeOnBoardingForm(instance=user)
        pinfo_form = PersonalInfoForm()
        return render(request, 'light/employee-onboarding.html', {
            'form': form,
            'pinfoForm': pinfo_form,
            'company': company,
            'uid': user.id
        })
    else:
        messages.warning(request, 'On boarding link is invalid. Ask your HR to resend the invite.')
        return redirect('login')


@require_POST
def on_boarding_new_employee(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        try:
            user = User.objects.get(pk=uid)
        except(User.DoesNotExist):
            user = None
        if user is not None:
            form = NewEmployeeOnBoardingForm(request.POST, request.FILES, instance=user)
            pinfo_form = PersonalInfoForm(request.POST)
            if form.is_valid() and pinfo_form.is_valid():
                cd = form.cleaned_data
                user.set_password(cd['confirm_password'])
                user.is_active = True
                user.on_boarding = True
                user.save()
                pinfo = pinfo_form.save(commit=False)
                pinfo.user = user
                pinfo.company = get_company_object_from_user(uid)
                pinfo.save()
                messages.success(request, 'Congratulation. On boarding is completed now. Please login')
                return redirect('login')
            else:
                company = get_company_object_from_user(uid)
                return render(request, 'light/employee-onboarding.html', {
                    'form': form,
                    'company': company,
                    'pinfoForm': pinfo_form,
                    'uid': uid
                })
        else:
            messages.warning(request,
                             'You are at wrong place. You are not legal candidate for this.' +
                             'Please Contact with HR. Thank you :-) ')
            return redirect('login')


@login_required
def view_my_profile(request, pk):
    company = get_company_object_from_user(request.user.id)
    if User.objects.filter(id=pk, role__name='Owner', company=company).exists():
        if pk != request.user.id:
            return render(request, 'light/error-404.html')

    access_profile = user_has_access(request.user.id, ['owner', 'new_employees'])
    if not access_profile:
        pk = request.user.id

    userProfile = get_object_or_404_template_default(User.objects
                                                     .select_related('department', 'designation', 'report_to')
                                                     .prefetch_related('user_emergency_contact',
                                                                       'user_edu_info', 'user_experience',
                                                                       'userfiles', 'user_bank'),
                                                     id=pk, company=company)  # .get(id=pk)

    projectsLeadBy = Project.objects.filter(lead_by=userProfile, company=company).select_related('lead_by').all()
    teamProjects = Project.objects.filter(team=userProfile, company=company).all()

    access_bank_info = user_has_access(request.user.id, ['owner', 'bank_info', 'payrolls'])
    b_context = {}
    if access_bank_info:
        # usersalary = UserSalary.objects.filter(user=pk, company=company).last()
        userBankinfo = BankInfo.objects.filter(user=pk, company=company).first()

        if request.method == 'POST':
            user_salary_form = UserSalaryForm(request.POST)
            user_bankinfo_form = BankInfoForm(request.POST, instance=userBankinfo)
            if user_salary_form.is_valid():
                user_salary = user_salary_form.save(commit=False)
                user_salary.company = company
                user_salary.user = userProfile
                user_salary.save()
            if user_bankinfo_form.is_valid():
                # print(user_bankinfo_form.cleaned_data)
                obj = user_bankinfo_form.save(commit=False)
                obj.user = userProfile
                obj.company = company
                obj.save()
            messages.success(request, 'Updated Successfully!')

        user_salary_form = UserSalaryForm()
        user_bankinfo_form = BankInfoForm(instance=userBankinfo)

        b_context = {'userSalaryForm': user_salary_form,
                     'userBankForm': user_bankinfo_form}

    user_salaries = UserSalary.objects.filter(user=pk, company=company)
    context = {'userProfile': userProfile,
               'projectsLeadBy': projectsLeadBy,
               'teamProjects': teamProjects,
               'user_salaries': user_salaries,
               **b_context
               }
    return render(request, 'light/profile.html', context)


def edit_salary_form(request, user_id, salary_id):
    company = get_company_object_from_user(request.user.id)
    user = get_object_or_404_template_default(User, id=user_id, company=company)
    if request.method == 'POST':
        salary = get_object_or_404_template_default(UserSalary, id=salary_id, company=company, user=user)
        form = UserSalaryForm(request.POST, instance=salary)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salary Update Successful!')
            return redirect('myprofile_detail', user_id)

    if request.is_ajax and request.method == 'GET':
        salary = get_object_or_404_template_default(UserSalary, id=salary_id, company=company, user=user)
        form = UserSalaryForm(instance=salary)
        form_string = render_to_string('salary_edit_form.html', {'form': form, 'salary': salary, 'salary_user': user},
                                       request)
        return JsonResponse({'salary_edit_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('myprofile_detail', user_id)


# class ViewEmployeeProfile(LoginRequiredMixin, generic.DetailView):
#     model = User
#     template_name = 'light/profile.html'
#
#     def get_queryset(self):
#         return User.objects.filter(id=self.kwargs.get('pk')) \
#             .select_related('department', 'designation', 'report_to') \
#             .prefetch_related('user_emergency_contact', 'user_edu_info', 'user_experience',
#                               'user_bank', 'salaries')


# working
class CompanyProfileUpdateView(LoginRequiredMixin, CompanyRequiredMixin, generic.edit.UpdateView):
    model = Company
    template_name = 'light/company_settings.html'
    fields = '__all__'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date_established'].widget = forms.DateInput(
            attrs={'type': 'date', 'value': datetime.datetime.now().date()}
        )
        form.fields['logo'].widget = forms.FileInput()
        return form

    def get_success_url(self):
        # obj = self.get_object()
        messages.success(self.request, 'Saved Successfully!')
        return reverse_lazy('mycompany_edit', args=[self.object.id])

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except:
            return render(request, 'light/error-404.html')

        if self.object.id == get_company_object_from_user(request.user.id).id:
            return super().get(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


@require_user_access_rights(['owner'])
@login_required
def localization(request):
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        currency_form = CurrencyForm(request.POST, instance=company)
        if currency_form.is_valid():
            currency_code = currency_form.cleaned_data['currency_code']
            currency_symbol = currency_sym[currency_code]
            currency_direction = currency_dir[currency_code]
            company.currency_code = currency_code
            company.currency_sym = currency_symbol
            company.currency_dir = currency_direction
            company.save()

            # print('{0}  {1}  {2}  '.format(currency_code, currency_symbol, currency_direction))
            messages.success(request, 'Localization Updated Successful!')

    currency_form = CurrencyForm(instance=company)
    return render(request, 'light/localization.html', {'form': currency_form})


# working
@login_required
def change_password(request):
    template_name = 'light/settings_password_change.html'
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, template_name, {'form': form})


@require_user_access_rights(['owner', 'department'])
@login_required
def company_departments(request):
    template_name = 'light/departments.html'
    company = get_company_object_from_user(request.user.id)
    departments = Department.objects.filter(company=company).all()
    return render(request, template_name, {'departments': departments})


@require_user_access_rights(['owner', 'department'])
@login_required
def create_n_edit_department(request, dep_id=None):
    if request.method == "POST":
        dep_name = request.POST['name'].strip()
        if dep_name not in (None, ''):
            if dep_id:
                dep = get_object_or_404_template_default(Department, id=dep_id)
                dep.name = dep_name
                dep.save()
                messages.success(request, 'Department Name Update Successful!')
            else:
                dep = Department.objects.create(name=dep_name, company=get_company_object_from_user(request.user.id))
                # dep.company = get_company_object_from_user(request.user.id)
                dep.save()
                messages.success(request, 'Department Addition Successful!')
        else:
            messages.error(request, 'Department name is empty')
    if request.is_ajax and request.method == 'GET':
        dep = get_object_or_404_template_default(Department, id=dep_id)
        form = DepartmentForm(instance=dep)
        form_string = render_to_string('departments-form.html', {'form': form, 'dep': dep}, request)
        return JsonResponse({'department_form': form_string}, status=200)
    return redirect('showDepartments')


# working
@require_user_access_rights(['owner', 'department'])
@login_required
def delete_department(request, dep_id=None):
    if dep_id is not None:
        try:
            dep = get_object_or_404_template_default(Department, id=dep_id)
            dep.delete()
        except ProtectedError:
            m = 'Deleting {0} will also delete its designations. Please make sure that all designations under {0} are not assigned to any employee.'.format(
                dep.name)
            messages.error(request, m)
            return redirect('showDepartments')

        messages.success(request, 'Department Deleted Successful!')
    return redirect('showDepartments')


@require_user_access_rights(['owner', 'designations'])
@login_required
def department_designations(request):
    template_name = 'light/designations.html'
    company = get_company_object_from_user(request.user.id)
    departments = Department.objects.filter(company=company).prefetch_related('designations')
    form = DesignationForm(company=company)
    return render(request, template_name, {'departments': departments, 'form': form})


@require_user_access_rights(['owner', 'designations'])
@login_required
def create_n_edit_designation(request, design_id=None):
    company = get_company_object_from_user(request.user.id)
    if request.method == "POST":
        if design_id:
            instance = get_object_or_404_template_default(Designation, id=design_id)
            form = DesignationForm(company=company, data=request.POST, instance=instance)
        else:
            form = DesignationForm(company=company, data=request.POST)
        if form.is_valid():
            dgn = form.save(commit=False)
            dgn.company = company
            dgn.save()
            if design_id:
                messages.success(request, 'Designation Update Successful!')
            else:
                messages.success(request, 'Designation Addition Successful!')
        else:
            messages.error(request, 'Unable to perform operation. Try again.')
    if request.is_ajax and request.method == 'GET':
        instance = get_object_or_404_template_default(Designation, id=design_id)
        form = DesignationForm(company=company, instance=instance)
        form_string = render_to_string('designations-form.html', {'form': form, 'dgn': instance}, request)
        return JsonResponse({'designation_form': form_string}, status=200)
    return redirect('showDesignations')


# working
@require_user_access_rights(['owner', 'designations'])
@login_required
def get_designation(request, dep_id=None):
    if request.is_ajax:
        if dep_id is not None:
            company = get_company_object_from_user(request.user.id)
            designations = list(
                Designation.objects.filter(department=dep_id, company=company).values_list('id', 'name', 'department'))

            return JsonResponse({'designations': designations}, status=200)

    return JsonResponse({'error': ''}, status=400)


# working
@require_user_access_rights(['owner', 'designations'])
@login_required
def delete_designation(request, design_id=None):
    company = get_company_object_from_user(request.user.id)
    if design_id is not None:
        try:
            dgn = get_object_or_404_template_default(Designation, id=design_id, company=company)
            dgn.delete()
        except ProtectedError:
            m = 'Designation will be deleted only if it is not assigned to any employee'
            messages.error(request, m)
            return redirect('showDesignations')

        messages.success(request, 'Designation Deleted Successful!')
    return redirect('showDesignations')


@require_user_access_rights(['owner', 'new_employees'])
@login_required
def get_user_profile_form(request, userID):
    company = get_company_object_from_user(request.user.id)
    access_role = user_has_access(request.user.id, ['owner', 'roles'])
    # print(request.method)
    if request.method == 'POST':
        # user = User.objects.prefetch_related('role').get(id=userID)
        user = get_object_or_404_template_default(User.objects.prefetch_related('role'), id=userID, company=company)
        # user = User.objects.filter(id=userID).prefetch_related('role').first()
        if access_role:
            form = ProfileInfoForm(request.POST, request.FILES, instance=user, company_name=company.name)
        else:
            form = ProfileInfoFormWithoutRole(request.POST, request.FILES, instance=user, company_name=company.name)

        # print(request.POST)
        if form.is_valid():
            # print(form.cleaned_data)
            usr = form.save(commit=False)

            owner_role = None
            for r in user.role.all():
                if r.name == 'Owner':
                    owner_role = r
                    break

            usr.save()
            form.save_m2m()
            if owner_role:
                usr.role.add(owner_role)
                usr.save()
            messages.success(request, 'User Profile Update Successful!')
            return redirect('myprofile_detail', userID)
        else:
            return redirect('myprofile_detail', userID)

    if request.is_ajax and request.method == 'GET':
        user = get_object_or_404_template_default(User.objects.select_related('department', 'designation', 'report_to'),
                                                  id=userID, company=company)
        # user = User.objects.filter(id=userID).select_related('department', 'designation', 'report_to').first()
        # user = User.objects.get(id=userID)#.prefetch_related('role').first()
        if access_role:
            form = ProfileInfoForm(instance=user, company_name=company.name, initial={'designation': user.designation})
            form_string = render_to_string('employee-profile-info-form.html',
                                           {'form': form, 'user': user}, request)
        else:
            form = ProfileInfoFormWithoutRole(instance=user, company_name=company.name,
                                              initial={'designation': user.designation})
            form_string = render_to_string('employee-profile-info-form-withoutRole.html',
                                           {'form': form, 'user': user}, request)
        return JsonResponse({'user_profile_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('myprofile_detail', userID)


@require_user_access_rights(['owner', 'new_employees'])
@login_required
def get_user_personal_info_form(request, userID):
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        info = get_object_or_404_template_default(PersonalInfo, user=userID, company=company)
        form = PersonalInfoForm(request.POST, instance=info)
        if form.is_valid():
            # print(form.cleaned_data)
            pinfo = form.save(commit=False)
            pinfo.company = company
            pinfo.save()
            messages.success(request, 'User Personal Info Update Successful!')
            return redirect('myprofile_detail', userID)

    if request.is_ajax and request.method == 'GET':
        user = get_object_or_404_template_default(User.objects.select_related('personalinfo'), id=userID,
                                                  company=company)
        form = PersonalInfoForm(instance=user.personalinfo)
        form_string = render_to_string('employee-personal-info-form.html', {'form': form, 'user': user}, request)
        return JsonResponse({'user_personalinfo_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('myprofile_detail', userID)


@require_user_access_rights(['owner', 'new_employees'])
@login_required
def get_user_emergency_contact_form(request, userID):
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        is_exist = EmergencyContact.objects.filter(user=userID, company=company).exists()
        if is_exist:
            emg = EmergencyContact.objects.get(user=userID, company=company)
            form = EmergencyContactForm(request.POST, instance=emg)
        else:
            form = EmergencyContactForm(request.POST)
        if form.is_valid():
            # print(form.cleaned_data)
            if is_exist:
                ec = form.save(commit=False)
                ec.company = company
                ec.save()
            else:
                user = get_object_or_404_template_default(User, id=userID, company=company)
                obj = form.save(commit=False)
                obj.user = user
                obj.company = company
                obj.save()
            messages.success(request, 'User Emergency Contact Update Successful!')
            return redirect('myprofile_detail', userID)

    if request.is_ajax and request.method == 'GET':
        user = get_object_or_404_template_default(User.objects.prefetch_related('user_emergency_contact'), id=userID,
                                                  company=company)
        form = EmergencyContactForm(instance=user.user_emergency_contact.first())
        form_string = render_to_string('employee-emergency-contact-form.html', {'form': form, 'user': user}, request)
        return JsonResponse({'user_emergency_contact_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('myprofile_detail', userID)


@require_user_access_rights(['owner', 'bank_info'])
@login_required
def get_user_bank_info_form(request, userID):
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        info = get_object_or_404_template_default(BankInfo, user=userID, company=company)
        form = BankInfoForm(request.POST, instance=info)
        if form.is_valid():
            # print(form.cleaned_data)
            bank_info = form.save(commit=False)
            bank_info.company = company
            bank_info.save()
            messages.success(request, 'User Bank Info Update Successful!')
            return redirect('myprofile_detail', userID)

    if request.is_ajax and request.method == 'GET':
        bankinfo_user = get_object_or_404_template_default(User, id=userID, company=company)
        info = get_object_or_404_template_default(BankInfo, user=userID, company=company)
        form = BankInfoForm(instance=info)
        form_string = render_to_string('employee-bank-info-form.html', {'userBankForm': form, 'bankinfo_user': bankinfo_user}, request)
        return JsonResponse({'user_bank_info_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('myprofile_detail', userID)


@login_required
def get_user_education_info_form(request, userID):
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        user = get_object_or_404_template_default(User, id=userID, company=company)
        formset = EducationInfoFormSet(request.POST, instance=user,
                                       queryset=EducationInfo.objects.filter(user=user, company=company).all())
        if formset.is_valid():
            forms1 = formset.save(commit=False)
            for f in forms1:
                f.company = company
                f.save()
            messages.success(request, 'User Education Information Update Successful!')
        else:
            messages.error(request, 'Unable to validate your form. Try again.')
        return redirect('myprofile_detail', userID)

    if request.is_ajax and request.method == 'GET':
        user = get_object_or_404_template_default(User, id=userID, company=company)
        # info = EducationInfo.objects.filter(user=user).values()
        # print(info)
        # formset = EducationInfoFormSet(initial=info, instance=user)

        formset = EducationInfoFormSet(queryset=EducationInfo.objects.filter(user=user, company=company).all(),
                                       instance=user)
        form_string = render_to_string('employee-education-info-form.html', {'formset': formset, 'user': user}, request)
        return JsonResponse({'user_education_info_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('myprofile_detail', userID)


@login_required
def get_user_experience_form(request, userID):
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        user = get_object_or_404_template_default(User, id=userID, company=company)
        formset = ExperienceFormSet(request.POST, instance=user,
                                    queryset=Experience.objects.filter(user=user, company=company).all())
        # print(request.POST)
        # print('==================================================================================')
        if formset.is_valid():
            # print(formset.cleaned_data)
            forms1 = formset.save(commit=False)
            for f in forms1:
                f.company = company
                f.save()
            messages.success(request, 'User Experience Update Successful!')
        else:
            messages.error(request, 'Unable to validate your form. Try again.')
        return redirect('myprofile_detail', userID)

    if request.is_ajax and request.method == 'GET':
        user = get_object_or_404_template_default(User, id=userID, company=company)
        formset = ExperienceFormSet(queryset=Experience.objects.filter(user=user, company=company).all(), instance=user)
        form_string = render_to_string('employee-experience-form.html', {'formset': formset, 'user': user}, request)
        return JsonResponse({'employee_experience_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('myprofile_detail', userID)


@login_required
def get_user_documents_form(request, userID):
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        user = get_object_or_404_template_default(User, id=userID, company=company)
        formset = UserFileFormSet(request.POST, request.FILES, instance=user,
                                  queryset=UserFile.objects.filter(user=user, company=company).all())
        # print(request.POST)
        # print('==================================================================================')
        if formset.is_valid():
            # print(formset.cleaned_data)
            forms1 = formset.save(commit=False)
            for f in forms1:
                f.company = company
                f.save()
            messages.success(request, 'User Document Update Successful!')
        else:
            messages.error(request, 'Unable to validate your form. Try again.')
        return redirect('myprofile_detail', userID)

    if request.is_ajax and request.method == 'GET':
        user = get_object_or_404_template_default(User, id=userID, company=company)
        formset = UserFileFormSet(queryset=UserFile.objects.filter(user=user, company=company).all(), instance=user)
        form_string = render_to_string('employee-documents-form.html', {'formset': formset, 'user': user}, request)
        return JsonResponse({'employee_document_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('myprofile_detail', userID)


@require_user_access_rights(['owner', 'new_clients'])
@login_required
def create_company_client(request):
    company = get_company_object_from_user(request.user.id)
    roles = Role.objects.filter(company=company).exclude(name='Owner')
    if request.method == 'POST':
        client_form = NewClientForm(request.POST, request.FILES)
        if client_form.is_valid():
            # print(client_form.cleaned_data)
            # return HttpResponse('okay')
            client = client_form.save(commit=False)
            client.company = company
            client.created_by = User.objects.get(company=company, id=request.user.id)
            client.save()
            username = str(client.email)
            username = username.split('@')[0]
            # roles = Role.objects.filter(id__in=[int(request.POST.get('role')), ])
            user, _ = User.objects.get_or_create(username=username, email=client.email, user_type=User.CLIENT,
                                                 password=make_password(request.POST.get('password')),
                                                 first_name=client.first_name, last_name=client.last_name,
                                                 is_active=True, company=company)
            try:
                role = Role.objects.get(name='all_company_clients_role__')
            except:
                messages.error(request, 'Please run create owner command first.')
                return redirect('view_clients')

            user.role.add(role)
            # basic = roles[0].role_permissions.filter(id=1)
            # roles[0].role_permissions.remove(basic[0].id)
            # for role in roles:
            #     user.role.add(role)
            user.save()
            client.user = user
            client.save()
            mail_subject = ('Complete your on-boarding for {0} company  account'.format(company.name))
            send_confirmation_mail_to_client(request, user, request.user, request.POST.get('password'),
                                             'registration/client_account_activation_by_email.html',
                                             mail_subject, client.email)
            messages.success(request, 'Stakeholder Addition Successful!')
            return redirect('view_clients')
        else:
            print('Unable to validate form')
    else:
        client_form = NewClientForm(initial={'client_code': get_client_custom_id(request)})
    return render(request, 'light/client-new.html', {'client_form': client_form, 'roles': roles})


@require_user_access_rights(['owner', 'new_clients'])
@login_required
def view_company_clients(request):
    company = get_company_object_from_user(request.user.id)
    clients = CompanyClient.objects.filter(company=company)
    # homeelement = baseelements(request)
    context1 = {'clients': clients}
    # context = {**homeelement, **context1}
    return render(request, 'light/clients.html', context1)


@require_user_access_rights(['owner', 'new_clients', 'projects'])
@login_required
def view_client_profile(request, client_id):
    company = get_company_object_from_user(request.user.id)
    if request.user.user_type == User.CLIENT:
        user_client = get_object_or_404_template_default(CompanyClient, email=request.user.email)
    else:
        user_client = get_object_or_404_template_default(CompanyClient, id=client_id, company=company)
    return render(request, 'light/client-profile.html', {'user_client': user_client})


@require_user_access_rights(['owner', 'new_clients'])
@login_required
def get_client_edit_form(request, client_id):
    company = get_company_object_from_user(request.user.id)
    if request.method == 'POST':
        client = get_object_or_404_template_default(CompanyClient, id=client_id, company=company)
        form = ClientEditForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client Update Successful!')
            return redirect('clientprofile_detail', client_id)

    if request.is_ajax and request.method == 'GET':
        client = get_object_or_404_template_default(CompanyClient, id=client_id, company=company)
        form = ClientEditForm(instance=client)
        form_string = render_to_string('client-edit-form.html', {'form': form, 'client': client}, request)
        return JsonResponse({'client_edit_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('clientprofile_detail', client_id)

class AnnouncementView(LoginRequiredMixin, View):

    template_name = 'announcements.html'
    form_class = NewAnnouncementForm

    def get(self, request):
        company = get_company_object_from_user(request.user.id)
        form = self.form_class
        announcements = Announcement.objects.filter(company=company)
        context = {'form': form, 'announcements': announcements}
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.company = get_company_object_from_user(request.user.id)
            announcement.announced_by = request.user
            announcement.save()
            messages.success(request, 'Client Addition Successful!')
            return redirect(reverse('announcements'))
        else:
            messages.error(request, 'Unable to validate form')
            return redirect(reverse('announcements'))

@login_required
def delete_announcement_list(request, *args, **kwargs):
    if Announcement.objects.filter(id=kwargs.get('pk')).exists():
        Announcement.objects.get(id=kwargs.get('pk')).delete()
    return redirect('announcements')


@login_required
def activateion_status(request, *args, **kwargs):
    if User.objects.filter(id=kwargs.get('pk')).exists():
        user = User.objects.filter(id=kwargs.get('pk')).first()
        if user.is_active is True:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
    return redirect('myprofile_detail', pk=kwargs.get('pk'))


@login_required
def color_picker(request):
    return render(request, 'light/color-picker.html')


@login_required
def change_timezone(request):
    if request.method == 'POST':
        timezone_str = request.POST['timezone']
        if timezone_str in pytz.common_timezones:
            try:
                user = User.objects.get(id=request.user.id)
                user.timezone = timezone_str
                user.save()
                messages.success(request, 'Timezone updated')
            except Exception as e:
                messages.error(request, 'Failed to update timezone')
    return render(request, 'light/timezone-selection.html', {'timezones': pytz.common_timezones})
