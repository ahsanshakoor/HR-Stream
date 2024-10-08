import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, ProtectedError
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.contrib import messages

from accounts.decorators import require_user_access_rights
from accounts.mixins import LeavePoliciesRequiredMixin
from accounts.models import User
from accounts.utils import get_company_object_from_user, get_object_or_404_template_default
from attendance.models import Attendance
from home.views import baseelements
from leave.form import LeavePolicyForm, LeaveForm, HolidayForm, DaysForm, LeaveRequestForm, LeaveRequestSearchForm, \
    EditLeaveRequestForm
from leave.models import WorkingDay, LeavePolicy, Leave, Holiday, LeaveRequest, LeaveStatistics


class LeavePolicyView(LoginRequiredMixin, LeavePoliciesRequiredMixin,  View):

    def get(self, request, *args, **kwargs):
        class_form = LeavePolicyForm
        template_name = 'leavePolicy.html'
        context = {'form': class_form}
        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        form_class = LeavePolicyForm(request.POST)
        if form_class.is_valid():
            leavePolicy = form_class.save(commit=False)
            leavePolicy.company = company
            leavePolicy.save()
            form_class = LeaveForm(initial={'leave_policy': leavePolicy})
            context = {'form': form_class, 'leavePolicy': leavePolicy }
            return redirect('leavepolicies')
        else:
            messages.error(request, 'Something Went Wrong')
            args = {}
            args['form'] = form_class
            return render(request, 'leavePolicy.html', args)


class LeaveView(LoginRequiredMixin, LeavePoliciesRequiredMixin,  View):

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        form_class = LeaveForm(request.POST)
        if form_class.is_valid():
            leave = form_class.save(commit=False)
            leave.company = company
            leave.save()
            form_class = LeaveForm(initial={'leave_policy': leave.leave_policy})
            context = {'form': form_class,  'leavePolicy': leave.leave_policy }
            return render(request, 'leaveType.html', context)
        else:
            args = {}
            args['form'] = form_class
            return render(request, 'leaveType.html', args)


# class HolidayView(LoginRequiredMixin, View):
#     class_form = HolidayForm
#     template_name = 'holiday.html'
#
#     def get(self, request, *args, **kwargs):
#         holiday = self.class_form
#         context = {'holiday': holiday}
#         return render(request, template_name=self.template_name, context=context)


# def holiday(request, *args, **kwargs):
#     if kwargs.get('pk'):
#         payroll = LeavePolicy.objects.get(id=kwargs.get('pk'))
#         data = {
#             'form-TOTAL_FORMS': '1',
#
#             'form-INITIAL_FORMS': '0',
#
#             'form-MAX_NUM_FORMS': '',
#
#             'form-0-leave_policy': payroll,
#         }
#         holiday_form = formset_factory(HolidayForm)
#         homeelement = baseelements(request)
#         context1 = {'holiday_form': holiday_form(data)}
#         context = {**homeelement, **context1}
#         return render(request, template_name='holiday.html', context=context)
#
#
# def addHolidays(request):
#     Form = formset_factory(HolidayForm)
#     holidayForm = Form(request.POST)
#     for holiday in holidayForm:
#         holiday.save()
#     return redirect(reverse('leavepolicyDetails'))


class EmployeeLeave(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        user = User.objects.get(id=request.user.id, company=company)
        leaves = Leave.objects.filter(company=company, leave_policy=user.leave_policy, is_active=True)

        leave_request = LeaveRequest.objects.filter(employee=user, company=company)
        remaining_days = 0
        leave_statics_list = []
        for leave in leaves:
            leave_static_dict = {}
            leave_statistics = LeaveStatistics.objects.filter(company=company, employee=user, leave_type=leave).select_related('leave_type').first()
            leave_static_dict['leave_static'] = leave_statistics
            leave_static_dict['current_leave'] = leave
            leave_statics_list.append(leave_static_dict)
            if leave_statistics is None:
                remaining_days = remaining_days + leave.days
            else:
                remaining_days = remaining_days + leave_statistics.remaining_days
        print(leave_statics_list)
        form_class = LeaveRequestForm(initial={'leave_type': leaves, 'requested_days': 1 })
        now = datetime.datetime.now().date()
        context = {'leave_user': user, 'leaves': leaves, 'form': form_class, 'remaining_days': remaining_days,
                   'leave_request': leave_request, 'now': now, 'leave_statics_list': leave_statics_list}
        return render(request, 'leave-employee.html', context)

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        user = User.objects.get(id=request.user.id, company=
                                company)
        leaves = Leave.objects.filter(leave_policy=user.leave_policy, company=company)
        leave_request = LeaveRequestForm(request.POST, initial={'leave_type': leaves })

        if leave_request.is_valid():
            print(leave_request)
            leave_from_date = leave_request.cleaned_data['leave_from']
            leave_to_date = leave_request.cleaned_data['leave_to']
            print(leave_from_date)
            print(leave_to_date)
            already_applied_date = LeaveRequest.objects.filter(employee=user, company=company, leave_from__gte=leave_from_date, leave_to__lte=leave_to_date).exists()

            if already_applied_date:
                messages.error(request, 'You already applied for the same date.')
                return redirect(reverse('leave'))

            leave_request = leave_request.save(commit=False)
            leave_request.employee = user
            leave_request.company = company
            leave_request.save()
            return redirect(reverse('leave'))
        else:
            leaves = Leave.objects.filter(company= company, leave_policy=user.leave_policy)
            context = {'user': user, 'leaves': leaves, 'form': leave_request}
            return render(request, 'leave-employee.html', context)


class AdminLeave(LoginRequiredMixin, LeavePoliciesRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        user = User.objects.get(company=company, id=request.user.id)
        users = User.objects.filter(company=company, report_to=user)
        users_count = User.objects.filter(company=company, report_to=user).count()
        leave_policy = LeavePolicy.objects.filter(company=company, is_active=True)
        leave_types = Leave.objects.filter(company=company, leave_policy__in=leave_policy)
        leaves = Leave.objects.filter(company=company, leave_policy=user.leave_policy)
        leave_request = LeaveRequest.objects.filter(company=company, employee__in=users)
        leave_statistics = LeaveStatistics.objects.filter(company=company, leave_type__in=leaves)
        remaining_days = LeaveStatistics.objects.filter(company=company, leave_type__in=leaves).aggregate(Sum('remaining_days'))
        remaining_days = remaining_days['remaining_days__sum']
        if not leave_statistics:
            remaining_days = Leave.objects.filter(company=company, leave_policy=user.leave_policy).aggregate(Sum('days'))
            remaining_days = remaining_days['days__sum']
        pending_request = LeaveRequest.objects.filter(company=company, employee__in=users, status=LeaveRequest.New).count()
        today_present = Attendance.objects.filter(company=company, employee__in=users, date=datetime.datetime.now().date()).count()
        form_class = LeaveRequestForm(initial={'leave_type': leaves})
        context = {'users': users,'user': user, 'leaves': leaves, 'form': form_class,
                   'remaining_days': remaining_days, 'leave_request': leave_request,
                   'leave_types': leave_types, 'pending_request': pending_request,
                   'today_present': today_present, 'users_count': users_count}
        return render(request, 'leave-admin.html', context)

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        user = User.objects.get(company=company, id=request.user.id)
        leave_request = LeaveRequestForm(request.POST)
        if leave_request.is_valid():
            leave_request = leave_request.save(commit=False)
            leave_request.employee = user
            leave_request.company = company
            leave_request.save()
            return redirect(reverse('leave'))
        else:
            leaves = Leave.objects.filter(leave_policy=user.leave_policy)
            context = {'user': user, 'leaves': leaves, 'form': leave_request}
            return render(request, 'leave-admin.html', context)


@require_user_access_rights(['owner', 'leave_policies'])
@login_required
def leaveRequestSearch(request):
    form_search = request.POST
    company = get_company_object_from_user(request.user.id)
    user = User.objects.get(id=request.user.id, company=company)
    users_count = User.objects.filter(report_to=user, company=company).count()
    users = User.objects.filter(report_to=user, company=company)
    leave_policy = LeavePolicy.objects.filter(company=company, is_active=True)
    leave_types = Leave.objects.filter(leave_policy__in=leave_policy, company=company)
    search_form = LeaveRequestSearchForm(initial={'employee': users, 'leave_type': leave_types})
    leaves = Leave.objects.filter(leave_policy=user.leave_policy, company=company)
    leave_from = datetime.datetime.strptime(form_search.get('leave-from'), '%d/%m/%Y').date()
    leave_to = datetime.datetime.strptime(form_search.get('leave-to'), '%d/%m/%Y').date()
    leave_request = LeaveRequest.objects.filter(employee_id=form_search.get('employee'), status=form_search.get('status'), leave_type_id=form_search.get('leave-type'), leave_from__gte=leave_from, leave_to__lte=leave_to, company=company)
    leave_statistics = LeaveStatistics.objects.filter(leave_type__in=leaves, company=company)
    remaining_days = LeaveStatistics.objects.filter(leave_type__in=leaves, company=company).aggregate(Sum('remaining_days'))
    remaining_days = remaining_days['remaining_days__sum']
    if not leave_statistics:
        remaining_days = Leave.objects.filter(leave_policy=user.leave_policy, company=company).aggregate(Sum('days'))
        remaining_days = remaining_days['days__sum']
    pending_request = LeaveRequest.objects.filter(employee__in=users, status=LeaveRequest.New, company=company).count()
    today_present = Attendance.objects.filter(employee__in=users, company=company).count()
    form_class = LeaveRequestForm(initial={'leave_type': leaves})
    context = {'user': user, 'leaves': leaves, 'form': form_class, 'remaining_days': remaining_days,
               'leave_request': leave_request, 'search_form': search_form, 'users': users,
               'leave_types': leave_types, 'pending_request': pending_request, 'today_present': today_present,
               'users_count': users_count}
    return render(request, 'leave-admin.html', context)

@require_user_access_rights(['owner', 'leave_policies'])
@login_required
def leaveStatus(request, request_id, name):
    company = get_company_object_from_user(request.user.id)
    try:
        leave_request = LeaveRequest.objects.get(id=request_id, company=company)
    except:
        messages.warning(request, 'Leave Request is deleted by employee')
        return redirect(reverse('leave_admin'))

    leave_type = Leave.objects.get(id=leave_request.leave_type.id, company=company)
    leave_statistics = LeaveStatistics.objects.filter(employee=leave_request.employee, leave_type=leave_type, company=company).first()
    if leave_request.status == name:
        messages.success(request, 'Status already set to '+name)
    elif leave_request.status == 'Approved':
        leave_statistics.remaining_days = leave_statistics.remaining_days + leave_request.requested_days
        leave_statistics.save()
        messages.success(request, 'Status is updated to ' + name)
    else:
        if leave_statistics is None:
            leave_statistics = LeaveStatistics()
            leave_statistics.employee = leave_request.employee
            leave_statistics.remaining_days = leave_type.days
            leave_statistics.leave_type = leave_type
            leave_statistics.company = company
            leave_statistics.save()
        if name == 'Approved':
         leave_statistics.remaining_days = leave_statistics.remaining_days - leave_request.requested_days
         leave_statistics.save()
    leave_request.status = name
    messages.success(request, 'Status is updated to '+name)
    leave_request.approved_by = request.user
    leave_request.save()
    return redirect(reverse('leave_admin'))


@login_required
def editLeaveRequest(request, pk, user):
    company = get_company_object_from_user(user.id)
    leave_request = LeaveRequest.objects.get(id=pk, company=company)
    if request.method == 'POST':
        form = EditLeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            l_request = form.save(commit=False)
            l_request.save()
            days = abs((l_request.leave_to - l_request.leave_from).days)
            l_request.requested_days = days
            l_request.company = company
            l_request.save()
            messages.success(request, 'Leave Request Update Successful!')
            if user == 'employee':
                return redirect('leave')
            else:
                return redirect('leave_admin')
        else:
            print(form.errors)
            messages.error(request, 'Leave Request Not Updated!')
            return redirect('task_board', pk)
    if request.is_ajax and request.method == 'GET':
        leaves = Leave.objects.filter(leave_policy=leave_request.employee.leave_policy, is_active=True, company=company)
        remaining_days = 0
        for leave in leaves:
            leave_statistics = LeaveStatistics.objects.filter(employee=leave_request.employee, leave_type=leave, company=company).first()
            if leave_statistics is None:
                remaining_days = remaining_days + leave.days
            else:
                remaining_days = remaining_days + leave_statistics.remaining_days
        now = datetime.datetime.now().date()
        form = EditLeaveRequestForm(instance=leave_request, initial={'leave_from': leave_request.leave_from, 'leave_to': leave_request.leave_to})
        form_string = render_to_string('editLeaveForm.html', {'form': form, 'pk': leave_request.id, 'user': user, 'remaining_days': remaining_days, 'now': now}, request)
        return JsonResponse({'leave_edit_form': form_string}, status=200)
    messages.error(request, 'Processing Error!. Try Again')
    if user == 'employee':
        return redirect('leave')
    else:
        return redirect('leave_admin')


@require_user_access_rights(['owner', 'basic'])
@login_required
def deleteLeaveRequest(request, pk, user):
    leave_request = None
    company = get_company_object_from_user(request.user.id)
    if LeaveRequest.objects.filter(company=company, id=pk).exists():
        leave_request = get_object_or_404_template_default(LeaveRequest, company=company, id=pk, status='New')
    if leave_request is not None:
        try:
            leave_request.delete()
            messages.success(request, 'Leave Request has been deleted')
        except ProtectedError as e:
            messages.error(request,
                           "Some Thing Went Wrong.Reload The Page")
    if user == 'employee':
        return redirect(reverse('leave'))
    else:
        return redirect(reverse('leave_admin'))


def getRemainingDays(request, pk, user):
    company = get_company_object_from_user(user.id)
    leave_statistics = LeaveStatistics.objects.filter(employee_id=user, leave_type_id=pk, company=company).first()
    leave = Leave.objects.get(id=pk)
    if leave_statistics is None:
        remaining_days = leave.days
    else:
        remaining_days = leave_statistics.remaining_days
    return JsonResponse({'remaining_days': remaining_days}, status=200)


class LeavePoliciesView(LoginRequiredMixin, LeavePoliciesRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        leave_policies = LeavePolicy.objects.filter(company=company)
        context = {'leave_policies': leave_policies}
        return render(request, 'leavePolicies.html', context)


@require_user_access_rights(['owner', 'leave_policies'])
@login_required
def leave_policy_status(request, pk, status):
    company = get_company_object_from_user(request.user.id)
    policy = LeavePolicy.objects.get(id=pk, company=company)
    state = 'Inactive'
    if status == 'True':
        state = 'Active'
    if policy.is_active == True and state == 'Active':
        messages.success(request, policy.name+' Policy is already '+state)
        return redirect('leavepolicies')
    elif policy.is_active == False and state == 'Inactive':
         messages.success(request, policy.name+' Policy is already '+state)
         return redirect('leavepolicies')
    else:
        policy.is_active = status
        policy.save()
        messages.success(request, policy.name+' Policy status updated to  '+state)
        return redirect('leavepolicies')


@require_user_access_rights(['owner', 'leave_policies'])
@login_required
def editLeavePolicy(request, *args, **kwargs):
    company = get_company_object_from_user(request.user.id)
    leave_policy = get_object_or_404_template_default(LeavePolicy, id=kwargs.get('pk'), company=company)
    form = LeavePolicyForm(instance=leave_policy)
    if request.POST:
        form = LeavePolicyForm(request.POST, instance=leave_policy)
        if form.is_valid():
            form.save()
            messages.success(request, leave_policy.name+' Leave Policy has been updated')
            return redirect(reverse('leavepolicies'))
        else:
            return render(request, 'editLeavePolicy.html', {'form': form, 'leave_policy_id': leave_policy.id})
    return render(request, 'editLeavePolicy.html', {'form': form, 'leave_policy_id': leave_policy.id})


def delete_leave_policy(request, pk):
    policy = None
    company = get_company_object_from_user(request.user.id)
    if LeavePolicy.objects.filter(company=company, id=pk).exists():
        policy = LeavePolicy.objects.get(company=company, id=pk)
    if policy is not None:
        try:
            policy.delete()
            messages.success(request, 'Leave Policy has been deleted')
        except ProtectedError as e:
            messages.error(request,
            policy.name + " Policy is  Assigned To Some Users. Unable to Delete This Leave Policy.")
    return redirect('leavepolicies')


def get_leave_type(request, pk):
    company = get_company_object_from_user(request.user.id)
    leavePolicy = get_object_or_404_template_default(LeavePolicy, id=pk, company=company)
    form_class = LeaveForm(initial={'leave_policy': leavePolicy})
    context = {'form': form_class, 'leavePolicy': leavePolicy}
    return render(request, 'leaveType.html', context)


@require_user_access_rights(['owner', 'leave_policies'])
@login_required
def edit_leave_type(request, **kwargs):
    company = get_company_object_from_user(request.user.id)
    leave = Leave.objects.get(id=kwargs.get('leave'), company=company)
    pk = leave.leave_policy.id
    if request.method == 'POST':
        form = LeaveForm(request.POST, instance=leave)
        if form.is_valid():
            board_form = form.save(commit=False)
            board_form.save()
            messages.success(request, leave.name + ' Updated Successful!')
            return redirect('/leavePolicyType/'+str(pk)+'/')
        else:
            messages.error(request, 'Leave Type Not Updated!')
            return redirect('/leavePolicyType/'+str(pk)+'/')

    if request.is_ajax and request.method == 'GET':
        form = LeaveForm(instance=leave)
        form_string = render_to_string('editLeaveTypeform.html', {'form': form, 'leave_id': leave.id, 'policy_id': pk}, request)
        return JsonResponse({'leave_type_edit_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('leavepolicies')


@require_user_access_rights(['owner', 'leave_policies'])
@login_required
def delete_leave_type(request, pk):
    leave_type = None
    company = get_company_object_from_user(request.user.id)
    if Leave.objects.filter(company=company, id=pk).exists():
        leave_type = get_object_or_404_template_default(Leave, company=company, id=pk)
    if leave_type is not None and LeaveStatistics.objects.filter(leave_type=leave_type, company=company).exists():
        LeaveStatistics.objects.filter(leave_type=leave_type, company=company).delete()
    if leave_type is not None and LeaveRequest.objects.filter(leave_type=leave_type, company=company).exists():
        LeaveRequest.objects.filter(leave_type=leave_type, company=company).delete()
    if leave_type is not None:
        try:
            leave_type.delete()
            messages.success(request, 'Leave Type has been deleted')
        except ProtectedError as e:
            messages.error(request, "Some Thing Went Wrong.Reload The Page")
    return redirect('get_leave_type', pk)


@require_user_access_rights(['owner', 'leave_policies'])
@login_required
def leave_type_status(request, pk, status):
    company = get_company_object_from_user(request.user.id)
    policy = Leave.objects.get(id=pk, company=company)
    id = policy.leave_policy.id
    state = 'Inactive'
    if status == 'True':
        state = 'Active'
    if policy.is_active is True and state == 'Active':
        messages.success(request, policy.name+' Policy is already '+state)
    elif policy.is_active is False and state == 'Inactive':
        messages.success(request, policy.name+' Policy is already '+state)
    else:
        policy.is_active = status
        policy.save()
        messages.success(request, policy.name+' Policy status updated to  '+state)
    return redirect('get_leave_type', id)
