import datetime
import logging
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.html import format_html
from num2words import num2words
import pendulum
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, ProtectedError, Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from accounts.decorators import require_user_access_rights
from accounts.mixins import PayrollsRequiredMixin
from accounts.models import User, UserSalary
from payroll.form import PayrollPolicyForm, PayrollItemForm, PayrollTaxItemForm, HealthInsuranceForm, \
    SalaryAdjustmentFormset, ManualPendingPayrollForm, ManualWorkHours, ClaimTypeForm, ClaimForm, ClaimFileForm, \
    ClaimFileFormSet
from payroll.models import Payroll, PayrollItem, PayrollPolicy, PayrollTaxItem, HealthInsurance, PendingPayrolls, \
    SalaryAdjustment, PayrollTax, ClaimType, Claim, ClaimFile
from accounts.utils import get_company_object_from_user, get_object_or_404_template_default
from payroll.serializers import PayrollSerializer
from payroll.utils import render_to_pdf
from timelog.models import TimeLog

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s"
)


class PayrollPolicyView(LoginRequiredMixin, PayrollsRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        form_class = PayrollPolicyForm
        context = {'form': form_class}
        return render(request, 'payroll-setting.html', context)

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        user = get_object_or_404_template_default(User, id=request.user.id, company=company)
        POST = request.POST.copy()
        POST['pay_period_end'] = POST['pay_period_end1']
        POST['pay_period_end_date'] = POST['pay_period_end_date1']
        payroll_policy_form = PayrollPolicyForm(POST)
        # print(request.POST)
        # print(POST)
        if payroll_policy_form.is_valid():
            print(payroll_policy_form.cleaned_data)
            payroll_policy = payroll_policy_form.save(commit=False)
            payroll_policy.company = company
            payroll_policy.created_by = user
            payroll_policy.next_pay_period_start_date = payroll_policy.pay_period_start_date
            payroll_policy.next_pay_period_end_date = payroll_policy.pay_period_end_date
            payroll_policy.save()
            return redirect('payroll_policies')
        else:
            return render(request, 'payroll-setting.html', {'form': payroll_policy_form})


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def payrollPolicies(request):
    company = get_company_object_from_user(request.user.id)
    payroll_policies = PayrollPolicy.objects.filter(company=company)
    context = {'payroll_policies': payroll_policies}
    return render(request, 'payroll-policy.html', context)


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def deletePayrollPolicy(request, pk):
    payroll_policy = None
    company = get_company_object_from_user(request.user.id)
    if PayrollPolicy.objects.filter(company=company, id=pk).exists():
        payroll_policy = PayrollPolicy.objects.get(company=company, id=pk)
    if payroll_policy is not None:
        try:
            payroll_policy.delete()
            messages.success(request, 'Payroll Policy has been deleted')
        except ProtectedError as e:
            messages.error(request,
                           payroll_policy.name + " is assigned to some employees")
    return redirect('payroll_policies')


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def editPayrollPolicyStatus(request, pk, status):
    company = get_company_object_from_user(request.user.id)
    payroll_policy = PayrollPolicy.objects.get(id=pk, company=company)
    if status == 'active':
        payroll_policy.policy_status = True

    elif status == 'inactive':
        payroll_policy.policy_status = False
    payroll_policy.save()
    messages.success(request, 'Payroll Policy has been updated to ' + status)
    return redirect('payroll_policies')


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def editPayrollPolicy(request, *args, **kwargs):
    company = get_company_object_from_user(request.user.id)
    payroll_policy = PayrollPolicy.objects.get(id=kwargs.get('pk'), company=company)
    form = PayrollPolicyForm(instance=payroll_policy)
    if request.POST:
        form = PayrollPolicyForm(request.POST, instance=payroll_policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll Policy has been updated')
            return redirect(reverse('payroll_policies'))
        else:
            return redirect('edit_payroll_policy', pk=payroll_policy.id)
    # return render(request, 'editPayroll-setting.html', {'form': form, 'payroll_policy_id': payroll_policy.id})
    return render(request, 'payroll-setting.html', {'form': form, 'payroll_policy_id': payroll_policy.id})


class PayrollItemView(LoginRequiredMixin, PayrollsRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        payroll_policy = get_object_or_404_template_default(PayrollPolicy, id=kwargs['pk'], company=company)
        benifit_form = PayrollItemForm(
            initial={'payroll_policy': payroll_policy, 'adjustment_type': PayrollItem.Benefit, 'is_active': False})
        deduction_form = PayrollItemForm(
            initial={'payroll_policy': payroll_policy, 'adjustment_type': PayrollItem.Deduction,
                     'is_active': False})
        overtime_form = PayrollItemForm(
            initial={'payroll_policy': payroll_policy, 'adjustment_type': PayrollItem.OverTime, 'is_active': False})
        tax_form = PayrollTaxItemForm(initial={'payroll_policy': payroll_policy, 'is_active': False})
        benifits = PayrollItem.objects.filter(payroll_policy=payroll_policy, adjustment_type=PayrollItem.Benefit,
                                              company=company)
        deductions = PayrollItem.objects.filter(payroll_policy=payroll_policy, adjustment_type=PayrollItem.Deduction,
                                                company=company)
        overtimes = PayrollItem.objects.filter(payroll_policy=payroll_policy, adjustment_type=PayrollItem.OverTime,
                                               company=company)
        taxes = PayrollTaxItem.objects.filter(payroll_policy=payroll_policy, company=company)
        context = {'befifit_form': benifit_form, 'deduction_form': deduction_form, 'overtime_form': overtime_form,
                   'benifits': benifits, 'deductions': deductions, 'overtimes': overtimes, 'tax_form': tax_form,
                   'taxes': taxes}
        return render(request, 'payroll-items.html', context)

    def post(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        user = User.objects.get(id=request.user.id, company=company)
        payroll_item_form = PayrollItemForm(request.POST)
        print(request.POST.get('adjustment_type'))
        if request.POST.get('adjustment_type') == 'OverTime':
            OverTime = PayrollItem.objects.filter(adjustment_type='OverTime', is_active=True, company=company).first()
            if OverTime is not None:
                messages.error(request, OverTime.name + ' is already active as overtime for this Payroll Policy')
                return redirect('payroll_item', pk=OverTime.payroll_policy.id)
        if payroll_item_form.is_valid():
            payroll_item = payroll_item_form.save(commit=False)
            payroll_item.created_by = user
            payroll_item.company = company
            payroll_item.save()
            messages.success(request, payroll_item.name + ' added successfully')
            return redirect('payroll_item', pk=payroll_item.payroll_policy.id)
        else:
            print(payroll_item_form)
            messages.error(request, 'form is invalid')
            return redirect(reverse('payroll_item'))


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def add_payroll_tax_item(request):
    company = get_company_object_from_user(request.user.id)
    user = User.objects.get(id=request.user.id, company=company)
    payroll_item_form = PayrollTaxItemForm(request.POST)
    if payroll_item_form.is_valid():
        payroll_item = payroll_item_form.save(commit=False)
        payroll_item.created_by = user
        payroll_item.company = company
        payroll_item.save()
        messages.success(request, payroll_item.name + ' added successfully')
        return redirect('payroll_item', pk=payroll_item.payroll_policy.id)
    else:
        print(payroll_item_form.errors)
        # messages.error(request, 'Tax form is invalid')
        # return redirect(reverse('payroll_item'))


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def edit_payroll_item(request, pk):
    company = get_company_object_from_user(request.user.id)
    payroll_item = PayrollItem.objects.get(id=pk, company=company)
    edit_form = request.POST
    payroll_item.name = edit_form.get('name')
    payroll_item.adjustment_type = edit_form.get('adjustment_type')
    if edit_form.get('is_active') == 'on':
        if payroll_item.adjustment_type == 'OverTime':
            OverTime = PayrollItem.objects.filter(payroll_policy=payroll_item.payroll_policy.id,
                                                  adjustment_type='OverTime', is_active=True, company=company).first()
            if OverTime is not None:
                messages.error(request, payroll_item.name + ' already active as overtime for this Payroll Policy')
                return redirect('payroll_item', pk=OverTime.payroll_policy.id)
        payroll_item.is_active = True
    else:
        payroll_item.is_active = False
    payroll_item.amount = edit_form.get('amount')
    payroll_item.save()
    messages.success(request, 'Payroll Policy has been updated')
    return redirect('payroll_item', pk=payroll_item.payroll_policy.id)


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def edit_tax_payroll_item(request, pk):
    company = get_company_object_from_user(request.user.id)
    payroll_item = PayrollTaxItem.objects.get(id=pk, company=company)
    edit_form = request.POST
    payroll_item.name = edit_form.get('name')
    if edit_form.get('is_active') == 'on':
        payroll_item.is_active = True
    else:
        payroll_item.is_active = False
    payroll_item.percentage = edit_form.get('amount')
    payroll_item.save()
    messages.success(request, 'Payroll Policy has been updated')
    return redirect('payroll_item', pk=payroll_item.payroll_policy.id)


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def delete_payroll_item(request, pk, policy_id):
    payroll_item = None
    payroll_item_type = None
    company = get_company_object_from_user(request.user.id)
    if PayrollItem.objects.filter(company=company, id=pk).exists():
        payroll_item = PayrollItem.objects.get(company=company, id=pk)
        payroll_item_type = payroll_item.adjustment_type
    if payroll_item is not None:
        try:
            payroll_item.delete()
            messages.success(request, 'Payroll Item has been deleted')
        except ProtectedError as e:
            messages.error(request,
                           payroll_item.name + "Some Thing Went Wrong.Reload The Page")
    return redirect('payroll_item', policy_id)


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def delete_payroll_tax_item(request, pk, policy_id):
    payroll_item = None
    company = get_company_object_from_user(request.user.id)
    if PayrollTaxItem.objects.filter(company=company, id=pk).exists():
        payroll_item = PayrollTaxItem.objects.get(company=company, id=pk)
    if payroll_item is not None:
        try:
            payroll_item.delete()
            messages.success(request, 'Payroll Item has been deleted')
        except ProtectedError as e:
            messages.error(request,
                           payroll_item.name + "Some Thing Went Wrong.Reload The Page")
    return redirect('payroll_item', policy_id)


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def editPayrollItemStatus(request, pk, status):
    company = get_company_object_from_user(request.user.id)
    payroll_item = PayrollItem.objects.get(company=company, id=pk)
    if status == 'active':
        if payroll_item.is_active == True:
            messages.success(request, 'Payroll Policy is already ' + status)
            return redirect('payroll_item', pk=payroll_item.payroll_policy.id)
        if payroll_item.adjustment_type == 'OverTime':
            OverTime = PayrollItem.objects.filter(company=company, payroll_policy=payroll_item.payroll_policy.id,
                                                  adjustment_type='OverTime', is_active=True).first()
            if OverTime is not None:
                messages.error(request, OverTime.name + ' already active as overtime for this Payroll Policy')
                return redirect('payroll_item', pk=OverTime.payroll_policy.id)
        payroll_item.is_active = True

    elif status == 'inactive':
        if payroll_item.is_active == False:
            messages.success(request, 'Payroll Policy is already ' + status)
            return redirect('payroll_item', pk=payroll_item.payroll_policy.id)
        payroll_item.is_active = False
    payroll_item.save()
    messages.success(request, 'Payroll Policy has been updated to ' + status)
    return redirect('payroll_item', pk=payroll_item.payroll_policy.id)


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def editPayrollTaxItemStatus(request, pk, status):
    company = get_company_object_from_user(request.user.id)
    payroll_item = PayrollTaxItem.objects.get(company=company, id=pk)
    if status == 'active':
        if payroll_item.is_active == True:
            messages.success(request, 'Payroll Policy is already ' + status)
            return redirect('payroll_item', pk=payroll_item.payroll_policy.id)
        payroll_item.is_active = True

    elif status == 'inactive':
        if payroll_item.is_active == False:
            messages.success(request, 'Payroll Policy is already ' + status)
            return redirect('payroll_item', pk=payroll_item.payroll_policy.id)
        payroll_item.is_active = False
    payroll_item.save()
    messages.success(request, 'Payroll Policy has been updated to ' + status)
    return redirect('payroll_item', pk=payroll_item.payroll_policy.id)


# def payroll_policy_status(request, pk, status):
#     policy = PayrollPolicy.objects.get(id=pk)
#     if policy.policy_status == status:
#         messages.success(request, 'Policy is already '+status)


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def pending_payroll_search(request):
    company = get_company_object_from_user(request.user.id)
    user_id = request.POST.get('user_id')
    start_date = request.POST.get('start_date')
    kquery = {}
    if start_date:
        kquery['start_date__gte'] = datetime.datetime.strptime(start_date, '%d/%m/%Y')
    end_date = request.POST.get('end_date')
    if end_date:
        kquery['end_date__lte'] = datetime.datetime.strptime(end_date, '%d/%m/%Y')
    print(user_id, kquery)
    if user_id:
        user = User.objects.get(id=user_id, company=company)
        kquery['user'] = user

    pending_payroll_form = ManualPendingPayrollForm(company=company)
    all_pending_payrolls = PendingPayrolls.objects.filter(company=company, **kquery).select_related(
        'user__payroll_policy')
    all_unpublished_payrolls = Payroll.objects.filter(company=company, published=False).select_related('user')
    all_published_payrolls = Payroll.objects.filter(company=company, published=True).select_related('user')
    search_users = User.objects.filter(company=company, user_type=User.EMPLOYEE).all()
    return render(request, 'pending_payrolls.html', {'all_pending_payrolls': all_pending_payrolls,
                                                     'pending_payroll_form': pending_payroll_form,
                                                     'all_unpublished_payrolls': all_unpublished_payrolls,
                                                     'all_published_payrolls': all_published_payrolls,
                                                     'search_users': search_users})


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def unpublished_payroll_search(request):
    company = get_company_object_from_user(request.user.id)
    user_id = request.POST.get('user_id')
    start_date = request.POST.get('start_date')
    kquery = {}
    if start_date:
        kquery['start_date__gte'] = datetime.datetime.strptime(start_date, '%d/%m/%Y')
    end_date = request.POST.get('end_date')
    if end_date:
        kquery['end_date__lte'] = datetime.datetime.strptime(end_date, '%d/%m/%Y')
    print(user_id, kquery)
    if user_id:
        user = User.objects.get(id=user_id, company=company)
        kquery['user'] = user

    pending_payroll_form = ManualPendingPayrollForm(company=company)
    all_pending_payrolls = PendingPayrolls.objects.filter(company=company).select_related('user__payroll_policy')
    all_unpublished_payrolls = Payroll.objects.filter(company=company, published=False, **kquery).select_related('user')
    all_published_payrolls = Payroll.objects.filter(company=company, published=True).select_related('user')
    search_users = User.objects.filter(company=company, user_type=User.EMPLOYEE).all()
    return render(request, 'pending_payrolls.html', {'all_pending_payrolls': all_pending_payrolls,
                                                     'pending_payroll_form': pending_payroll_form,
                                                     'all_unpublished_payrolls': all_unpublished_payrolls,
                                                     'all_published_payrolls': all_published_payrolls,
                                                     'search_users': search_users})


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def published_payroll_search(request):
    company = get_company_object_from_user(request.user.id)
    # user_id = request.POST.get('user_id')
    user_id = request.GET.get('user_id')
    start_date = request.GET.get('start_date')
    # start_date = request.POST.get('start_date')
    kquery = {}

    if start_date:
        kquery['start_date__gte'] = datetime.datetime.strptime(start_date, '%d/%m/%Y')

    end_date = request.GET.get('end_date')
    # end_date = request.POST.get('end_date')
    if end_date:
        kquery['end_date__lte'] = datetime.datetime.strptime(end_date, '%d/%m/%Y')

    if user_id:
        user = User.objects.get(id=user_id, company=company)
        kquery['user'] = user
    print(kquery)
    pending_payroll_form = ManualPendingPayrollForm(company=company)
    all_pending_payrolls = PendingPayrolls.objects.filter(company=company).select_related('user__payroll_policy')
    all_unpublished_payrolls = Payroll.objects.filter(company=company, published=False).select_related('user')
    all_published_payrolls = Payroll.objects.filter(company=company, published=True, **kquery).select_related('user')
    search_users = User.objects.filter(company=company, user_type=User.EMPLOYEE).all()
    return render(request, 'pending_payrolls.html', {'all_pending_payrolls': all_pending_payrolls,
                                                     'pending_payroll_form': pending_payroll_form,
                                                     'all_unpublished_payrolls': all_unpublished_payrolls,
                                                     'all_published_payrolls': all_published_payrolls,
                                                     'search_users': search_users})


class PayrollSalaryView(LoginRequiredMixin, PayrollsRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        now = timezone.now().date()

        policies = PayrollPolicy.objects.filter(company=company)
        for policy in policies:
            while now > policy.next_pay_period_end_date:
                policy_users = User.objects.filter(payroll_policy=policy,
                                                   company=company,
                                                   user_type=User.EMPLOYEE,
                                                   is_active=True)
                if policy_users:
                    for user in policy_users:
                        pending_payroll = PendingPayrolls()
                        pending_payroll.company = company
                        pending_payroll.user = user
                        pending_payroll.start_date = policy.next_pay_period_start_date
                        pending_payroll.end_date = policy.next_pay_period_end_date
                        pending_payroll.save()

                    policy_end_date = pendulum.date(policy.next_pay_period_end_date.year,
                                                    policy.next_pay_period_end_date.month,
                                                    policy.next_pay_period_end_date.day)

                    policy.next_pay_period_start_date = policy_end_date.add(days=1)
                    if policy.payroll_cycle == PayrollPolicy.WEEKLY:
                        policy.next_pay_period_end_date = policy_end_date.add(days=7)
                    elif policy.payroll_cycle == PayrollPolicy.BI_WEEKLY:
                        policy.next_pay_period_end_date = policy_end_date.add(days=14)
                    elif policy.payroll_cycle == PayrollPolicy.MONTHLY:
                        if policy.pay_period_end == 32:
                            policy.next_pay_period_end_date = policy_end_date.add(days=1).end_of('month')
                        else:
                            policy.next_pay_period_end_date = policy_end_date.end_of('month').add(
                                days=policy.pay_period_end)
                    elif policy.payroll_cycle == PayrollPolicy.BI_MONTHLY:
                        if policy.next_pay_period_end_date.day == 15:
                            policy.next_pay_period_end_date = policy_end_date.end_of('month')
                        else:
                            policy.next_pay_period_end_date = policy_end_date.replace(day=15)

                    policy.save()
                else:
                    break
        search_type = ''
        kquery = {}
        if request.GET.get('search'):
            search_type = request.GET.get('search_type')
            user_id = request.GET.get('user_id')
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            if start_date:
                kquery['start_date__gte'] = datetime.datetime.strptime(start_date, '%d/%m/%Y')

            if end_date:
                kquery['end_date__lte'] = datetime.datetime.strptime(end_date, '%d/%m/%Y')

            if user_id:
                user = User.objects.get(id=user_id, company=company)
                kquery['user'] = user

        pending_payroll_form = ManualPendingPayrollForm(company=company)
        if search_type == 'pending':
            all_pending_payrolls = PendingPayrolls.objects.filter(company=company, **kquery).select_related(
                'user__payroll_policy')
        else:
            all_pending_payrolls = PendingPayrolls.objects.filter(company=company).select_related(
                'user__payroll_policy')
        if search_type == 'unpublish':
            all_unpublished_payrolls = Payroll.objects.filter(company=company, published=False,
                                                              **kquery).select_related('user')
        else:
            all_unpublished_payrolls = Payroll.objects.filter(company=company, published=False).select_related('user')

        if search_type == 'publish':
            all_published_payrolls = Payroll.objects.filter(company=company, published=True, **kquery).select_related(
                'user')
        else:
            all_published_payrolls = Payroll.objects.filter(company=company, published=True).select_related('user')

        search_users = User.objects.filter(company=company, user_type=User.EMPLOYEE).all()
        return render(request, 'pending_payrolls.html', {'all_pending_payrolls': all_pending_payrolls,
                                                         'pending_payroll_form': pending_payroll_form,
                                                         'all_unpublished_payrolls': all_unpublished_payrolls,
                                                         'all_published_payrolls': all_published_payrolls,
                                                         'search_users': search_users})


def get_previous_payroll_cycle(cycle_type, start_date, pay_period_end):
    policy_start_date = pendulum.date(start_date.year, start_date.month, start_date.day)
    # policy_end_date = pendulum.date(end_date.year, end_date.month, end_date.day)

    final_end_date = policy_start_date.subtract(days=1)
    final_start_date = None
    if cycle_type == PayrollPolicy.WEEKLY:
        final_start_date = policy_start_date.subtract(days=7)

    elif cycle_type == PayrollPolicy.BI_WEEKLY:
        final_start_date = policy_start_date.subtract(days=14)

    elif cycle_type == PayrollPolicy.MONTHLY:
        if pay_period_end == 32:
            final_start_date = final_end_date.start_of('month')
        else:
            final_start_date = policy_start_date.subtract(months=1)

    elif cycle_type == PayrollPolicy.BI_MONTHLY:
        if final_end_date.day == 15:
            final_start_date = final_end_date.start_of('month')
        else:
            final_start_date = final_end_date.replace(day=16)

    return {
        'final_start_date': final_start_date,
        'final_end_date': final_end_date
    }


def get_payroll_custom_id(request):
    previous_payroll = Payroll.objects.filter(company=get_company_object_from_user(request.user.id)).last()
    if previous_payroll is None:
        p_code = 'PAY-0001'
    else:
        p_code = previous_payroll.payroll_code
        if p_code in ('', None):
            p_code = 'PAY-0000'
            # previous_payroll.payroll_code = p_code
            # previous_payroll.save()
        p_code_str = p_code[4:]
        p_code = 'PAY-{0:04d}'.format(int(p_code_str) + 1)
    return p_code


def employee_payrolls(request):
    company = get_company_object_from_user(request.user.id)
    payrolls = Payroll.objects.filter(user=request.user, company=company, published=True) \
        .prefetch_related('payroll_taxes', 'payroll_salary_adjustments')

    return render(request, 'employee_payrolls.html', {'payrolls': payrolls})


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def manually_add_payroll(request):
    if request.method == 'POST':
        company = get_company_object_from_user(request.user.id)
        form = ManualPendingPayrollForm(request.POST, company=company)
        if form.is_valid():
            # print(form.cleaned_data)
            obj = form.save(commit=False)
            obj.company = company
            obj.save()
            messages.success(request, 'Pending Payroll has been Added')
            return redirect('payroll_salary')


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def generate_salary_slip(request, pay_id):
    if request.method == 'POST':
        company = get_company_object_from_user(request.user.id)
        payroll_id = None
        # getcontext().prec = 2
        try:
            pendingPayroll = get_object_or_404_template_default(
                PendingPayrolls.objects.select_related('user__payroll_policy'),
                id=pay_id, company=company)

            if pendingPayroll.user.payroll_policy is None:
                messages.error(request, 'Payroll Policy is not assigned to this employee')
                return redirect('payroll_salary')

            user = pendingPayroll.user

            formset = SalaryAdjustmentFormset(request.POST)
            payroll = Payroll(user=pendingPayroll.user, company=company, start_date=pendingPayroll.start_date,
                              end_date=pendingPayroll.end_date)
            payroll.save()
            payroll_id = payroll.id
            adj_benefit = 0
            adj_deduction = 0
            adj_claim = 0
            if formset.is_valid():
                print(formset)
                for f in formset:
                    cd = f.cleaned_data

                    if cd['adjustment_type'] == SalaryAdjustment.Benefit:
                        adj_benefit += abs(cd['amount'])
                    elif cd['adjustment_type'] == SalaryAdjustment.Deduction:
                        adj_deduction += abs(cd['amount'])
                    else:
                        adj_claim += abs(cd['amount'])

                    obj = SalaryAdjustment()
                    obj.name = cd['name']
                    obj.amount = cd['amount']
                    obj.adjustment_type = cd['adjustment_type']
                    obj.payroll = payroll
                    obj.company = company
                    obj.user = pendingPayroll.user
                    obj.save()

            payroll_policy_items = PayrollItem.objects.filter(company=company,
                                                              payroll_policy=pendingPayroll.user.payroll_policy,
                                                              is_active=True)
            payroll_policy_tax_items = PayrollTaxItem.objects.filter(company=company,
                                                                     payroll_policy=pendingPayroll.user.payroll_policy,
                                                                     is_active=True)
            # Saving Payroll Policy Items to SalaryAdjustments ( SalaryAdjustment objects are related to Employee Payroll )
            for item in payroll_policy_items:
                i = SalaryAdjustment(
                    payroll=payroll,
                    company=company,
                    user=pendingPayroll.user,
                    name=item.name,
                    amount=item.amount,
                    adjustment_type=item.adjustment_type,
                )
                i.save()

            # If Employee Salary is Hourly based
            hour_form = ManualWorkHours(request.POST)
            extra_salary_amount = 0
            if hour_form.is_valid():
                hours = abs(hour_form.cleaned_data['hours'])
                if hours:
                    salary = UserSalary.objects.filter(company=company, user=user).last().salary
                    extra_salary_amount = salary * Decimal(hours)
                    payroll.overtime = hours
                    payroll.overtime_amount = Decimal(extra_salary_amount)
                else:
                    payroll.overtime = 0

            # Calculate Gross and Net Salary
            cents = Decimal('.01')
            gross_salary = pendingPayroll.working_hours_salary + pendingPayroll.benefit_amount + \
                           Decimal(adj_benefit) + Decimal(extra_salary_amount)

            gross_salary = gross_salary.quantize(cents, ROUND_HALF_UP)

            net_salary = gross_salary - pendingPayroll.deduction_amount - Decimal(adj_deduction)
            net_salary = net_salary.quantize(cents, ROUND_HALF_UP)

            taxes_amount = 0

            # Saving Payroll Policy Taxitems to PayrollTax ( PayrollTax objects are related to Employee Payroll )
            for item in payroll_policy_tax_items:
                tax_amount = (gross_salary * Decimal(item.percentage)) / 100
                i = PayrollTax(
                    payroll=payroll,
                    company=company,
                    user=pendingPayroll.user,
                    name=item.name,
                    percentage=item.percentage,
                    tax_amount=tax_amount,
                )
                i.save()
                net_salary -= tax_amount
                taxes_amount += tax_amount

            if user.apply_401k_before_tax:
                _401K_amount = (gross_salary * Decimal(user.percentage_401k)) / 100
            else:
                _401K_amount = (net_salary * Decimal(user.percentage_401k)) / 100

            net_salary -= _401K_amount
            # net_salary = net_salary.quantize(cents, ROUND_HALF_UP)

            previous_cycle = get_previous_payroll_cycle(pendingPayroll.user.payroll_policy.payroll_cycle,
                                                        pendingPayroll.start_date,
                                                        pendingPayroll.user.payroll_policy.pay_period_end)

            all_claims = Claim.objects.filter(
                company=company, user=user,
                status=Claim.Approved,
                date__gte=previous_cycle['final_start_date'],
                date__lte=previous_cycle['final_end_date']).select_related('claim_type')
            all_claims_amount = all_claims.aggregate(Sum('amount'))['amount__sum']
            if all_claims_amount is None:
                all_claims_amount = 0

            net_salary += abs(Decimal(all_claims_amount)) + Decimal(adj_claim)
            net_salary = net_salary.quantize(cents, ROUND_HALF_UP)

            # Saving Claims to SalaryAdjustments ( SalaryAdjustment objects are related to Employee Payroll )
            for item in all_claims:
                i = SalaryAdjustment(
                    payroll=payroll,
                    company=company,
                    user=pendingPayroll.user,
                    name=item.claim_type.name,
                    amount=item.amount,
                    adjustment_type=SalaryAdjustment.CLAIM,
                )
                i.save()

            payroll.payroll_code = get_payroll_custom_id(request)
            payroll.amount_401K = _401K_amount
            payroll.gross_salary = gross_salary
            payroll.net_salary = net_salary
            payroll.working_hours = pendingPayroll.working_hours
            payroll.save()
            pendingPayroll.delete()
            messages.success(request, 'Payroll Creation for {0} is Successful'.format(user.get_full_name()))
            return redirect('payroll_salary')
            # payroll1 = Payroll.objects.filter(company=company, user=user, id=payroll.id).select_related('user') \
            #     .prefetch_related('payroll_salary_adjustments', 'payroll_taxes').first()
            #
            # totals = get_all_payroll_totals(payroll1)
            # return render(request, 'SalarySlip.html', {'payroll': payroll1, **totals})
        except Exception as e:
            print(e)
            if payroll_id and Payroll.objects.filter(company=company, id=payroll_id).exists():
                Payroll.objects.get(company=company, id=payroll_id).delete()
            messages.error(request, 'Unable to create payroll. Try again.')
            return redirect('payroll_salary')


# @require_user_access_rights(['owner', 'payrolls'])
# @login_required
def get_all_payroll_totals(payroll):
    total_benefits = 0
    total_deductions = 0
    total_taxes_amount = 0
    total_claims_amount = 0
    for b in payroll.payroll_salary_adjustments.all():
        if b.adjustment_type == SalaryAdjustment.Benefit:
            total_benefits += abs(b.amount)
        elif b.adjustment_type == SalaryAdjustment.Deduction:
            total_deductions += abs(b.amount)
        elif b.adjustment_type == SalaryAdjustment.CLAIM:
            total_claims_amount += abs(b.amount)

    for t in payroll.payroll_taxes.all():
        total_taxes_amount += abs(t.tax_amount)
    all_total_deductions = total_deductions + total_taxes_amount + payroll.amount_401K
    return {
        'total_benefits': total_benefits,
        'total_deductions': total_deductions,
        'total_taxes_amount': total_taxes_amount,
        'all_total_deductions': all_total_deductions,
        'total_claims_amount': total_claims_amount}


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def veiw_salary_slip(request, user_id, payroll_id):
    company = get_company_object_from_user(request.user.id)
    user_payroll = get_object_or_404_template_default(User, id=user_id, company=company)
    payroll = get_object_or_404_template_default(Payroll.objects.select_related('user')
                                                 .prefetch_related('payroll_salary_adjustments', 'payroll_taxes'),
                                                 company=company, user=user_payroll, id=payroll_id)
    # Payroll.objects.filter(company=company, user=user_payroll, id=payroll_id).select_related('user') \
    #     .prefetch_related('payroll_salary_adjustments', 'payroll_taxes').first()

    totals = get_all_payroll_totals(payroll)
    context = {'payroll': payroll, **totals}
    context1 = {**context, 'payroll_context': context}
    return render(request, 'SalarySlip.html', context=context1)


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def download_pay_slip(request, user_id, payroll_id):
    company = get_company_object_from_user(request.user.id)
    user_payroll = get_object_or_404_template_default(User, id=user_id, company=company)
    payroll = get_object_or_404_template_default(Payroll.objects.select_related('user')
                                                 .prefetch_related('payroll_salary_adjustments', 'payroll_taxes'),
                                                 company=company, user=user_payroll, id=payroll_id)

    totals = get_all_payroll_totals(payroll)
    context = {'payroll': payroll, **totals, 'user': request.user}

    return render_to_pdf('download_payslip.html', context)

    # context1 = {**context, 'payroll_context': context}
    # return render(request, 'SalarySlip.html', context=context1)


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def calculate_salary_slip(request, pay_id):
    company = get_company_object_from_user(request.user.id)
    pendingPayroll = get_object_or_404_template_default(
        PendingPayrolls.objects.select_related('user__payroll_policy'), id=pay_id, company=company)
    user = pendingPayroll.user
    user_payroll_policy = user.payroll_policy

    if user_payroll_policy is None:
        messages.error(request, 'Payroll Policy is not assigned to this employee')
        return redirect('payroll_salary')

    leave_hours = 0

    # calculate production hour and overtime
    production_time = 0

    # salary calculation
    payroll_cycle_type = {PayrollPolicy.WEEKLY: 52,
                          PayrollPolicy.BI_WEEKLY: 26,
                          PayrollPolicy.MONTHLY: 12,
                          PayrollPolicy.BI_MONTHLY: 24,
                          }
    try:
        salary_object = user.salaries.last()
        basic_salary = Decimal(salary_object.salary)
        salary_amount = Decimal(0)
        # getcontext().prec = 28
        if salary_object.salary_type == UserSalary.YEARLY:
            salary_amount = basic_salary / Decimal(payroll_cycle_type[user_payroll_policy.payroll_cycle])
        elif salary_object.salary_type == UserSalary.MONTHLY:
            salary_amount = basic_salary
        elif salary_object.salary_type == UserSalary.HOURLY:
            timelogs = TimeLog.objects.filter(company=company, name=user)
            production_time = timelogs.aggregate(Sum('start_time'))['start_time__sum']
            if production_time is not None:
                total_hours = production_time.total_seconds()
                h = total_hours / 3600
                # m = (total_hours % 3600) // 60
                # total_hours = "%d.%d" % (h, m)
                production_time = Decimal(h)
            else:
                production_time = Decimal(0)
            salary_amount = production_time * basic_salary

        benefit_sum = PayrollItem.objects.filter(company=company, payroll_policy=user_payroll_policy,
                                                 adjustment_type=PayrollItem.Benefit,
                                                 is_active=True).aggregate(Sum('amount'))
        benefit_sum = benefit_sum['amount__sum']
        if benefit_sum is None:
            benefit_sum = 0

        deduction_sum = PayrollItem.objects.filter(company=company, payroll_policy=user_payroll_policy,
                                                   adjustment_type=PayrollItem.Deduction,
                                                   is_active=True).aggregate(Sum('amount'))
        deduction_sum = deduction_sum['amount__sum']
        if deduction_sum is None:
            deduction_sum = 0

        taxes_percentage_sum = PayrollTaxItem.objects.filter(company=company, payroll_policy=user_payroll_policy,
                                                             is_active=True).aggregate(Sum('percentage'))
        taxes_percentage_sum = taxes_percentage_sum['percentage__sum']
        if taxes_percentage_sum is None:
            taxes_percentage_sum = 0

        pendingPayroll.benefit_amount = benefit_sum
        pendingPayroll.deduction_amount = deduction_sum
        pendingPayroll.taxes_percentage = taxes_percentage_sum
        pendingPayroll.working_hours_salary = salary_amount
        pendingPayroll.working_hours = production_time
        pendingPayroll.leave_hours = leave_hours
        pendingPayroll.save()

        benefits = PayrollItem.objects.filter(company=company, payroll_policy=user_payroll_policy,
                                              adjustment_type=PayrollItem.Benefit,
                                              is_active=True)
        deductions = PayrollItem.objects.filter(company=company, payroll_policy=user_payroll_policy,
                                                adjustment_type=PayrollItem.Deduction,
                                                is_active=True)
        all_taxes = PayrollTaxItem.objects.filter(company=company, payroll_policy=user_payroll_policy,
                                                  is_active=True)

        cents = Decimal('.01')
        dec_benefit_sum = Decimal(benefit_sum)
        gross_salary = Decimal(salary_amount) + Decimal(benefit_sum)
        logging.error('USER_DEFINED: gross_salary => {0}, salary_amount => {1}, dec_benefit_sum => {2}'.format(
            gross_salary, salary_amount, dec_benefit_sum))
        try:
            gross_salary = gross_salary.quantize(cents, ROUND_HALF_UP)
        except Exception as e:
            logging.exception(str(e))
            gross_salary = Decimal(round(gross_salary, 2))

        taxes_amount = (gross_salary * Decimal(taxes_percentage_sum)) / 100
        taxes_amount = taxes_amount.quantize(cents, ROUND_HALF_UP)

        net_salary = gross_salary - Decimal(taxes_amount) - Decimal(deduction_sum)
        net_salary = net_salary.quantize(cents, ROUND_HALF_UP)

        if user.apply_401k_before_tax:
            _401K_amount = (gross_salary * Decimal(user.percentage_401k)) / 100
        else:
            _401K_amount = (net_salary * Decimal(user.percentage_401k)) / 100

        net_salary -= _401K_amount
        net_salary = net_salary.quantize(cents, ROUND_HALF_UP)

        all_taxes_amounts = {}

        for t in all_taxes:
            tax_amount = (gross_salary * Decimal(t.percentage)) / 100
            all_taxes_amounts[t.name] = tax_amount.quantize(cents, ROUND_HALF_UP)

        previous_cycle = get_previous_payroll_cycle(user_payroll_policy.payroll_cycle,
                                                    pendingPayroll.start_date, user_payroll_policy.pay_period_end)

        all_claims = Claim.objects.filter(
            company=company, user=user,
            status=Claim.Approved,
            date__gte=previous_cycle['final_start_date'],
            date__lte=previous_cycle['final_end_date']).select_related('claim_type')
        all_claims_amount = all_claims.aggregate(Sum('amount'))['amount__sum']
        if all_claims_amount is None:
            all_claims_amount = 0

        net_salary += abs(Decimal(all_claims_amount))
        net_salary = net_salary.quantize(cents, ROUND_HALF_UP)

        net_salary_words = num2words(net_salary)

        formset = SalaryAdjustmentFormset()
        hour_form = ManualWorkHours(initial={'hours': 0})
        context = {
            'pendingPayroll': pendingPayroll,
            'gross_salary': gross_salary,
            'net_salary': net_salary,
            'net_salary_words': net_salary_words,
            'benefits': benefits,
            'deductions': deductions,
            'taxes_amount': taxes_amount,
            'amount_401K': _401K_amount,
            'all_taxes_amounts': all_taxes_amounts,
            'formset': formset,
            'hour_form': hour_form,
            'salary_type': salary_object.salary_type,
            'all_claims': all_claims,
            'all_claims_amount': all_claims_amount

        }
        return render(request, 'salary_slip_details.html', context=context)
    except Exception as e:
        logging.exception(str(e))
        messages.warning(request, 'Unable to calculate. Please Try Again.')
        return redirect('payroll_salary')


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def editPayrollPublish(request, pk, status):
    company = get_company_object_from_user(request.user.id)
    payroll = Payroll.objects.get(id=pk, company=company)
    state = 'Unpublished'
    if status == 'True':
        state = 'Published'
    if payroll.published == True and state == 'Published':
        messages.success(request, payroll.payroll_code + ' Payroll is already ' + state)
        return redirect('payroll_salary')
    elif payroll.published == False and state == 'Unpublished':
        messages.success(request, payroll.payroll_code + ' Payroll is already ' + state)
        return redirect('payroll_salary')
    elif status == 'True':
        payroll.published = True
    elif status == 'False':
        payroll.published = False
    payroll.save()
    messages.success(request, payroll.payroll_code + ' Payroll status updated to  ' + state)
    return redirect('payroll_salary')


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def deletePayroll(request, pk):
    company = get_company_object_from_user(request.user.id)
    payroll = None
    if Payroll.objects.filter(id=pk, company=company).exists():
        payroll = Payroll.objects.get(id=pk, company=company)
    if payroll is not None:
        try:
            payroll.delete()
            messages.success(request, 'Payroll has been Deleted')
        except Exception as e:
            print(e)
            messages.error(request, 'Unable to Delete Payroll')
    return redirect('payroll_salary')


@require_user_access_rights(['owner', 'payrolls'])
@login_required
def deletePendingPayroll(request, pk):
    company = get_company_object_from_user(request.user.id)
    payroll = None
    if PendingPayrolls.objects.filter(id=pk, company=company).exists():
        payroll = PendingPayrolls.objects.get(id=pk, company=company)
    if payroll is not None:
        try:
            payroll.delete()
            messages.success(request, 'Pending Payroll has been Deleted')
        except Exception as e:
            print(e)
            messages.error(request, 'Unable to Delete Pending Payroll')
    return redirect('payroll_salary')

@require_user_access_rights(['owner', 'health_insurance'])
@login_required
def health_insurance_create(request):
    if request.method == 'POST':
        company = get_company_object_from_user(request.user.id)
        user = get_object_or_404_template_default(User, id=request.user.id, company=company)
        form = HealthInsuranceForm(request.POST)
        if form.is_valid():
            health_ins = form.save(commit=False)
            health_ins.company = company
            health_ins.created_by = user
            health_ins.save()
            messages.success(request, 'Health Insurance created successful!')
            return redirect('health_insurances')
        else:
            return render(request, 'health_insurance_form.html', {'form': form})

    form = HealthInsuranceForm()
    return render(request, 'health_insurance_form.html', {'form': form})


@require_user_access_rights(['owner', 'health_insurance'])
@login_required
def health_insurance_edit(request, pk):
    company = get_company_object_from_user(request.user.id)
    health_ins = get_object_or_404_template_default(HealthInsurance, id=pk, company=company)
    form = HealthInsuranceForm(instance=health_ins)
    if request.method == 'POST':
        form = HealthInsuranceForm(request.POST, instance=health_ins)
        if form.is_valid():
            form.save()
            messages.success(request, 'Health Insurance has been updated')
            return redirect('health_insurances')
        else:
            return redirect('health_insurance_edit', pk=pk)
    return render(request, 'health_insurance_form.html', {'form': form, 'health_insurance_id': health_ins.id})


@require_user_access_rights(['owner', 'health_insurance'])
@login_required
def health_insurance_delete(request, pk):
    company = get_company_object_from_user(request.user.id)
    health_ins = get_object_or_404_template_default(HealthInsurance, id=pk, company=company)
    if health_ins is not None:
        try:
            health_ins.delete()
            messages.success(request, 'Health Insurance has been deleted')
        except ProtectedError as e:
            messages.error(request, 'This policy is assigned to a user')
    return redirect('health_insurances')


@require_user_access_rights(['owner', 'health_insurance'])
@login_required
def health_insurance_status_edit(request, pk, status):
    company = get_company_object_from_user(request.user.id)
    health_ins = HealthInsurance.objects.get(id=pk, company=company)
    if status == 'active':
        health_ins.active = True
    elif status == 'inactive':
        health_ins.active = False
    health_ins.save()
    messages.success(request, 'Health Insurance has been updated to ' + status)
    return redirect('health_insurances')


@require_user_access_rights(['owner', 'health_insurance'])
@login_required
def healthInsurances(request):
    company = get_company_object_from_user(request.user.id)
    health_insurances = HealthInsurance.objects.filter(company=company).select_related('created_by')
    context = {'health_insurances': health_insurances}
    return render(request, 'health_insurances.html', context)


@login_required
def get_detail_for_payroll(request, payroll_id=None):
    company = get_company_object_from_user(request.user.id)
    if request.is_ajax and request.method == 'GET':
        if payroll_id is not None:
            query_set = Payroll.objects.filter(id=payroll_id, user=request.user, company=company)
            payroll = Payroll.objects.filter(company=company, user=request.user, id=payroll_id) \
                .prefetch_related('payroll_salary_adjustments', 'payroll_taxes').first()
            gross_salary = payroll.gross_salary
            amount_401K = payroll.amount_401K
            all_payroll = get_all_payroll_totals(payroll)
            benefit = all_payroll['total_benefits']
            deduction = all_payroll['total_deductions']
            claim = all_payroll['total_claims_amount']
            tax = all_payroll['total_taxes_amount']
            benefit_percentage = 0
            deduction_percentage = 0
            tax_percentage = 0
            claim_percentage = 0
            gross_amount_percentage = 0
            amount_401K_percentage = 0
            if gross_salary is not None or 0:
                if amount_401K != 0:
                    amount_401K_percentage = round((amount_401K / gross_salary) * 100, 2)
                else:
                    amount_401K = 0
                if benefit != 0:
                    benefit_percentage = round((benefit / gross_salary) * 100, 2)
                if deduction != 0:
                    deduction_percentage = round((deduction / gross_salary) * 100, 2)
                if tax != 0:
                    tax_percentage = round((tax / gross_salary) * 100, 2)
                if claim != 0:
                    claim_percentage = round((claim / gross_salary), 2)

                gross_amount = Decimal(gross_salary) - Decimal(deduction) - Decimal(benefit) - Decimal(tax) - Decimal(
                    amount_401K)
                try:
                    gross_amount_percentage = round((gross_amount / Decimal(gross_salary)) * 100, 2)
                except:
                    try:
                        gross_amount_percentage = (gross_amount / Decimal(gross_salary)) * 100
                        gross_amount_percentage = gross_amount_percentage.quantize(Decimal('.01'), ROUND_HALF_UP)
                    except:
                        logging.error(
                            f'Gross Amount => {gross_amount}, Gross Salary => {gross_salary}, Deduction => {deduction}, Benefit => {benefit}, Tax => {tax}, 401K Amount => {amount_401K}, Gross Amount Percentage => {gross_amount_percentage}')
            data_list = []
            dict = {'name': 'Basic Salary', 'y': int(gross_amount_percentage), 'sliced': True, 'selected': True}
            if int(gross_amount_percentage) != 0:
                data_list.append(dict)
            dict = {'name': 'Deduction', 'y': int(deduction_percentage)}
            if int(deduction_percentage) != 0:
                data_list.append(dict)
            dict = {'name': 'Benifit', 'y': int(benefit_percentage)}
            if int(benefit_percentage) != 0:
                data_list.append(dict)
            dict = {'name': 'Tax', 'y': int(tax_percentage)}
            if int(tax_percentage) != 0:
                data_list.append(dict)
            dict = {'name': '401K', 'y': int(amount_401K_percentage)}
            if int(amount_401K_percentage) != 0:
                data_list.append(dict)
            dict = {'name': 'claim', 'y': int(claim_percentage)}
            if int(claim_percentage) != 0:
                data_list.append(dict)
            payrolls = PayrollSerializer(query_set, many=True).data
            return JsonResponse({'payroll': payrolls, 'data_list': data_list}, status=200)
    return JsonResponse({'error': ''}, status=400)


@require_user_access_rights(['owner', 'claim'])
@login_required
def company_claim_type(request):
    company = get_company_object_from_user(request.user.id)
    claim_types = ClaimType.objects.filter(company=company).all()
    return render(request, 'claim-type.html', {'claim_types': claim_types})


@require_user_access_rights(['owner', 'claim'])
@login_required
def create_n_edit_claim_type(request, claim_type_id=None):
    if request.method == "POST":
        claim_type_name = request.POST['name'].strip()
        if claim_type_name not in (None, ''):
            if claim_type_id:
                claim_type = get_object_or_404_template_default(ClaimType, id=claim_type_id)
                claim_type.name = claim_type_name
                claim_type.save()
                messages.success(request, 'ClaimType Name Update Successful!')
            else:
                claim_type = ClaimType.objects.create(name=claim_type_name,
                                                      company=get_company_object_from_user(request.user.id))
                claim_type.save()
                messages.success(request, 'ClaimType Addition Successful!')
        else:
            messages.error(request, 'ClaimType name is empty')
    if request.is_ajax and request.method == 'GET':
        claim_type = get_object_or_404_template_default(ClaimType, id=claim_type_id)
        form = ClaimTypeForm(instance=claim_type)
        form_string = render_to_string('claim_type_form.html', {'form': form, 'claim_type': claim_type}, request)
        return JsonResponse({'claim_form': form_string}, status=200)
    return redirect('showClaimType')


# working

@require_user_access_rights(['owner', 'claim'])
@login_required
def delete_claim_type(request, claim_type_id=None):
    if claim_type_id is not None:
        try:
            claim_type = get_object_or_404_template_default(ClaimType, id=claim_type_id)
            claim_type.delete()
        except ProtectedError:
            m = 'Deleting {0} will also delete its designations. Please make sure that all designations under {0} are not assigned to any employee.'.format(
                claim_type.name)
            messages.error(request, m)
            return redirect('showClaimType')

        messages.success(request, 'ClaimType Deleted Successful!')
    return redirect('showClaimType')


@require_user_access_rights(['owner', 'claim'])
@login_required
def company_claims_admin(request):
    template_name = 'claim_admin.html'
    company = get_company_object_from_user(request.user.id)
    users = User.objects.filter(company=company, report_to=request.user)
    claims = Claim.objects.filter(company=company, user__in=users)
    return render(request, template_name, {'claims': claims, 'users': users})


@login_required
def company_claims(request):
    template_name = 'claim.html'
    company = get_company_object_from_user(request.user.id)
    form = ClaimForm(company_name=company.name)
    formImage = ClaimFileForm()
    claims = Claim.objects.filter(company=company, user=request.user).all()
    return render(request, template_name, {'claims': claims, 'form': form, 'formImage': formImage})


@login_required
def create_n_edit_claim(request, claim_id=None):
    company = get_company_object_from_user(request.user.id)
    if request.method == "POST":
        if claim_id:
            claim = Claim.objects.filter(id=claim_id, company=company).first()
            file = ClaimFile.objects.filter(company=company, claim=claim)
            fileformset = ClaimFileFormSet(request.POST, request.FILES, instance=claim, queryset=file)
            claim_form = ClaimForm(request.POST, company_name=company.name, instance=claim)
            if claim_form.is_valid() and fileformset.is_valid():
                claim_form.save()
                fileformset.save()
                messages.success(request, 'Claim Name Update Successful!')
            else:
                messages.success(request, 'SomeThing Went Wrong!')
        else:
            claim_form = ClaimForm(request.POST, company_name=company.name)
            file_form = ClaimFileForm(request.POST.get('file'), request.FILES)
            if claim_form.is_valid() and file_form.is_valid():
                claim = claim_form.save(commit=False)
                claim.user = request.user
                claim.company = company
                claim.save()
                for f in request.FILES.getlist('file'):
                    file_type = f.content_type.split('/')[0]
                    print(file_type)
                    instance = ClaimFile(claim=claim, file=f, type=file_type, company=company)
                    instance.save()
                messages.success(request, 'Claim Addition Successful!')
            else:
                messages.success(request, 'SomeThing Went Wrong!')
    if request.is_ajax and request.method == 'GET':
        claim = get_object_or_404_template_default(Claim, id=claim_id)
        form = ClaimForm(company_name=company.name, instance=claim)
        # fileformset = ProjectFileFormSet(instance=project, queryset=file)
        form_string = render_to_string('claim-form.html', {'form': form, 'claim': claim}, request)
        return JsonResponse({'claim_form': form_string}, status=200)
    return redirect('showClaims')


@login_required
def delete_claim(request, claim_id=None):
    if claim_id is not None:
        try:
            claim = get_object_or_404_template_default(Claim, id=claim_id)
            claim.delete()
        except ProtectedError:
            m = 'Deleting {0} will also delete its designations. Please make sure that all designations under {0} are not assigned to any employee.'.format(
                claim.name)
            messages.error(request, m)
            return redirect('showClaims')

        messages.success(request, 'Claim Deleted Successful!')
    return redirect('showClaims')


@login_required
def claim_status(request, request_id, name):
    company = get_company_object_from_user(request.user.id)
    try:
        claim = Claim.objects.get(id=request_id, company=company)
        if claim.status == name:
            messages.success(request, 'Status already set to ' + name)
        else:
            claim.status = name
            messages.success(request, 'Status is updated to ' + name)
            claim.save()
        return redirect('showClaimsAdmin')
    except:
        messages.warning(request, 'Claim is deleted by employee')
        return redirect('showClaimsAdmin')


@login_required
def get_claim_files(request, claim_id=None):
    company = get_company_object_from_user(request.user.id)
    if request.is_ajax:
        claim = get_object_or_404_template_default(Claim, id=claim_id)
        claim_files = ClaimFile.objects.filter(company=company, claim=claim)
        form_string = render_to_string('claim_files.html', {'claim_files': claim_files}, request)
        return JsonResponse({'claim_files': form_string}, status=200)
    return redirect('showClaimsAdmin')


@login_required
def claim_search(request):
    user_id = request.POST.get('user_id')
    status = request.POST.get('status')
    date = request.POST.get('claim_date')

    company = get_company_object_from_user(request.user.id)
    if user_id:
        user = User.objects.get(id=user_id, company=company)
    else:
        user = None
    if date:
        date = datetime.datetime.strptime(request.POST.get('claim_date'), '%d/%m/%Y').date()
    else:
        date = None
    users = User.objects.filter(company=company, report_to=request.user)
    claims = Claim.objects.filter(company=company, user__in=users)
    claims = claims.filter(Q(user=user) | Q(status=status) | Q(date=date))
    context = {'users': users, 'claims': claims, 'users': users}
    return render(request, 'claim_admin.html', context=context)
