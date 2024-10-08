import datetime
from decimal import Decimal, getcontext
import pendulum as pendulum
import pytz
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone as tz, timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, ProtectedError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.html import format_html

from accounts.decorators import require_user_access_rights
from accounts.mixins import AttendancePoliciesRequiredMixin
from accounts.models import User
from accounts.utils import get_company_object_from_user, get_object_or_404_template_default
from payroll.models import PayrollPolicy
from .models import Attendance, AttendancePunch, Shift, AttendancePolicy
from django.views import View
from .forms import AttendancePolicyForm, ShiftForm
import pendulum
from accounts.templatetags.accounts_tags import subtract, subtractTime


def get_employee_overtime(attendance, company):
    over_time = 0.0
    time_in = AttendancePunch.objects.filter(attendance=attendance, company=company).first().in_time
    time_out = AttendancePunch.objects.filter(attendance=attendance, company=company).last().out_time
    if attendance.employee.attendance_policy:
        working_hour = attendance.employee.attendance_policy.working_hour
    else:
        return over_time

    # print(subtractTime(time_out, time_in))
    # print(working_hour)

    if attendance.employee.attendance_policy.working_hour_policy == 'Normal':
        if time_out is None:
            return 0
        if subtractTime(time_out, time_in) > working_hour:
            if subtract(subtractTime(time_out, time_in), working_hour) > 0:
                if subtract(subtractTime(time_out, time_in),
                            working_hour) > attendance.employee.attendance_policy.overtime:
                    over_time = subtract(subtractTime(time_out, time_in), working_hour)

    elif attendance.employee.attendance_policy.working_hour_policy == 'Strict':
        if subtract(attendance.total_duration, working_hour) > 0:
            if subtract(attendance.total_duration, working_hour) > attendance.employee.attendance_policy.overtime:
                over_time = subtract(attendance.total_duration, working_hour)

    return over_time


class AttendanceView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        template_name = 'attendance-employee.html'
        to_day = pendulum.now()
        company = get_company_object_from_user(request.user.id)
        today_attendance = Attendance.objects.filter(employee=request.user, date=datetime.date.today(), company=company).first()
        attendance_punch = AttendancePunch.objects.filter(attendance=today_attendance, company=company)
        attendance_punch_last = AttendancePunch.objects.filter(attendance=today_attendance, company=company).last()
        month_attendance = Attendance.objects.filter(employee=request.user,
                                                     date__gte=datetime.date.today().replace(day=1), company=company)
        month_production = Attendance.objects.filter(employee=request.user,
                                                     date__gte=datetime.date.today().replace(day=1), company=company).aggregate(
            Sum('total_duration'))
        if month_production['total_duration__sum'] is None:
            month_production['total_duration__sum'] = 0

        start_of_month = to_day.start_of('month')
        end_of_month = to_day.end_of('month')
        days_in_month = getWeekdaysNumber(start_of_month, end_of_month)
        daily_production_hour = 0
        if request.user.attendance_policy is not None:
            daily_production_hour = request.user.attendance_policy.working_hour

        weekly_production_hour = daily_production_hour * 5  # 5 is no of week days
        month_production_hour = daily_production_hour * days_in_month
        month_production_percentage = 0
        if month_production_hour != 0:
            month_production_percentage = (month_production['total_duration__sum'] / month_production_hour) * 100
        start_of_week = to_day.start_of('week')
        week_production = Attendance.objects.filter(employee=request.user, created_at__gte=start_of_week).aggregate(
            Sum('total_duration'))
        if week_production['total_duration__sum'] is None:
            week_production['total_duration__sum'] = 0
        week_production_percentage = 0
        if weekly_production_hour != 0:
            week_production_percentage = (week_production['total_duration__sum'] / weekly_production_hour) * 100
        today_production_percentage = 0
        if today_attendance is not None:
            if daily_production_hour != 0:
                today_production_percentage = (today_attendance.total_duration / daily_production_hour) * 100

        monthly_attendance_list = []
        count = 0
        for attendance in month_attendance:
            month_attendance_punch_in = AttendancePunch.objects.filter(attendance=attendance, company=company).first()
            month_attendance_punch_last = AttendancePunch.objects.filter(attendance=attendance, company=company).last()
            production = AttendancePunch.objects.filter(attendance=attendance, company=company).aggregate(Sum('duration'))
            count += 1

            overtime = get_employee_overtime(attendance, get_company_object_from_user(request.user.id))

            monthly_attendance_dict = {
                "id": count,
                'attendance': attendance,
                'in_time': month_attendance_punch_in.in_time,
                'out_time': month_attendance_punch_last.out_time,
                'production': production,
                'overtime': overtime
            }
            monthly_attendance_list.append(monthly_attendance_dict)
        context = {'today_attendance': today_attendance, 'attendance_punch': attendance_punch,
                   'attendance_punch_last': attendance_punch_last,
                   'month_attendance': monthly_attendance_list, 'm_production': month_production['total_duration__sum'],
                   'w_production': week_production['total_duration__sum'], 'm_percentage': month_production_percentage,
                   'w_perentage': week_production_percentage,
                   't_percentage': today_production_percentage,
                   'r_percentage': 100 - month_production_percentage,
                   'r_production': month_production_hour - month_production['total_duration__sum'],
                   'daily_production_hour': daily_production_hour,
                   'weekly_production_hour': weekly_production_hour,
                   'month_production_hour': month_production_hour}
        return render(request, template_name=template_name, context=context)


@login_required
def punchIn(request):
    company = get_company_object_from_user(request.user.id)
    today = timezone.now().replace(tzinfo=None)
    _attendance = Attendance.objects.filter(date=today.date(), employee=request.user, company=company).first()
    if not _attendance:
        today_attendance = Attendance()
        today_attendance.date = today.date()
        today_attendance.employee = request.user
        today_attendance.total_break = 0.00
        today_attendance.total_duration = 0.00
        today_attendance.company = company
        today_attendance.save()
        punch = AttendancePunch()
        punch.attendance = today_attendance
        punch.in_time = today.time()
        punch.company = company
        punch.save()
    else:
        last_punch = AttendancePunch.objects.filter(attendance=_attendance, company=company).last()
        dateTimeB = datetime.datetime.combine(today.date(), last_punch.out_time)
        time_difference = today - dateTimeB
        getcontext().prec = 3
        hour_break = Decimal(time_difference.total_seconds() / 3600)
        _attendance.total_break = _attendance.total_break + hour_break
        _attendance.save()
        punch = AttendancePunch()
        punch.attendance = _attendance
        punch.in_time = today.time()
        punch.company = company
        punch.save()
    return redirect(reverse('attendance'))



@login_required
def punchOut(request):
    today = timezone.now().replace(tzinfo=None)
    company = get_company_object_from_user(request.user.id)
    attendance = Attendance.objects.filter(date=today.date(), employee=request.user, company=company).first()
    last_punch = AttendancePunch.objects.filter(attendance=attendance, company=company).last()
    if last_punch:
        last_punch.out_time = today.time()
        last_punch.save()
    else:
        return redirect(reverse('attendance'))
    dateTimeA = datetime.datetime.combine(today.date(), last_punch.out_time)
    dateTimeB = datetime.datetime.combine(today.date(), last_punch.in_time)
    time_difference = dateTimeA - dateTimeB
    getcontext().prec = 3
    time_difference = Decimal(time_difference.total_seconds() / 3600)
    attendance.total_duration = attendance.total_duration + time_difference

    # user = User.objects.filter(id=request.user.id, company=company).select_related('attendance_policy')
    # if user.attendance_policy.working_hour_policy == AttendancePolicy.Normal:
    #     first_punch = AttendancePunch.objects.filter(attendance=attendance, company=company).first()
    #     dateTimeC = datetime.datetime.combine(datetime.date.today(), first_punch.in_time)
    #     attendance.total_duration = dateTimeA - dateTimeC

    attendance.save()
    return redirect(reverse('attendance'))

@login_required
def attendanceSearch(request):
    template_name = 'attendance-employee.html'
    company = get_company_object_from_user(request.userid)
    today_attendance = Attendance.objects.filter(employee=request.user, date=datetime.date.today(), company=company).first()
    attendance_punch = AttendancePunch.objects.filter(attendance=today_attendance, company=company)
    attendance_punch_last = AttendancePunch.objects.filter(attendance=today_attendance, company=company).last()
    if request.GET.get('attendance_date'):
        date_day = datetime.datetime.strptime(request.GET.get('attendance_date'), '%d/%m/%Y').day

    searched = Attendance.objects.filter(employee=request.user, company=company)
    if request.GET.get('attendance_year'):

        searched = Attendance.objects.filter(id__in=searched, date__year=request.GET.get('attendance_year'), company=company)
        if request.GET.get('attendance_month'):

            searched = Attendance.objects.filter(id__in=searched, date__month=request.GET.get('attendance_month'), company=company)
            if request.GET.get('attendance_date'):
                print('year date')
                searched = Attendance.objects.filter(id__in=searched, date__day=date_day, company=company)
    elif request.GET.get('attendance_month'):
        print('month')
        searched = Attendance.objects.filter(id__in=searched, date__month=request.GET.get('attendance_month'))
        if request.GET.get('attendance_date'):
            print('month date')
            searched = Attendance.objects.filter(id__in=searched, date__day=date_day, company=company)
    elif request.GET.get('attendance_date'):
        print('date')
        searched = Attendance.objects.filter(id__in=searched,
                                             date=datetime.datetime.strptime(request.GET.get('attendance_date'),
                                                                             '%d/%m/%Y'), company=company)
    else:
        print('nothing')

    searched_attendance_list = []
    count = 0
    for attendance in searched:
        month_attendance_punch_in = AttendancePunch.objects.filter(attendance=attendance, company=company).first()
        month_attendance_punch_last = AttendancePunch.objects.filter(attendance=attendance, company=company).last()
        count += 1
        monthly_attendance_dict = {
            "id": count,
            'attendance': attendance,
            'in_time': month_attendance_punch_in.in_time,
            'out_time': month_attendance_punch_last.out_time,
        }
        searched_attendance_list.append(monthly_attendance_dict)
    context = {'today_attendance': today_attendance, 'attendance_punch': attendance_punch,
               'attendance_punch_last': attendance_punch_last, 'month_attendance': searched_attendance_list}
    return render(request, template_name=template_name, context=context)


class AttendancePoilcyView(LoginRequiredMixin, AttendancePoliciesRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        template_name = 'attendance-settings.html'
        form_class = AttendancePolicyForm(request)
        shifts = Shift.objects.filter(company=get_company_object_from_user(request.user.id)).count()
        if shifts == 0:
            message = format_html(
                'Please Add Shift For Company First <a href="{}" class="btn add-btn"> Go To Shift</a>',
                reverse('shift'))
            messages.error(request, message)
            return redirect('attendance_policies')
        context = {'form': form_class}
        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        form_class = AttendancePolicyForm(request, request.POST)
        if form_class.is_valid():
            attendancePolicy = form_class.save(commit=False)
            attendancePolicy.company = get_company_object_from_user(request.user.id)
            attendancePolicy.created_by = request.user
            attendancePolicy.save()
            return redirect(reverse('attendance_policies'))
        else:
            args = {}
            args['form'] = form_class
            return render(request, 'attendance-settings.html', args)


class AttendanceAdminView(LoginRequiredMixin, AttendancePoliciesRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        template_name = 'attendance-admin.html'
        company = get_company_object_from_user(request.user.id)
        users = company.users.filter(user_type=User.EMPLOYEE).all()
        dates = dates_of_month()
        now = pendulum.now().date() #tz.now().date()
        end_of_month = pendulum.now().end_of('month').day

        attendance = []
        for user in users:
            # print(user)
            attendance_list = []
            for date in dates:
                # print(date)
                attendance_obj = Attendance.objects.filter(employee=user, date=date, company=company).first()
                attendance_list.append(attendance_obj)
            attendance_dict = {
                'user': user,
                'attendance': attendance_list
            }
            attendance.append(attendance_dict)

        context = {'users': users, 'attendance_list': attendance, 'now': now, 'end_of_month': end_of_month}
        return render(request, template_name, context)


def dates_of_month():
    date_list = []
    today = pendulum.now()
    start = today.start_of('month')
    end = today
    period = pendulum.period(start, end)
    for dt in period.range('days'):
        date_list.append(dt)
    return date_list

    # count = 0
    # date = datetime.date.replace(start)
    #
    # while date < end:
    #     count += 1
    #     date = date.replace(day=count)
    #     date_list.append(date)
    # return date_list


@require_user_access_rights(['owner', 'attendance_policies'])
@login_required
def employeeAttendanceSearch(request):
    template_name = 'attendance-admin.html'
    company = get_company_object_from_user(request.user.id)
    users = company.users.all()
    user = User.objects.get(id=request.GET.get('user'), company=company)
    today = pendulum.now()
    year = int(request.GET.get('year'))
    month = int(request.GET.get('month'))

    date_list = []
    start = pendulum.datetime(year, month, 1)
    if today.month == month:
        end = today
    else:
        end = start.end_of('month')
    period = pendulum.period(start, end)
    for dt in period.range('days'):
        date_list.append(dt)

    attendance_list = []
    attendance = []
    for date in date_list:
        attendance_obj = Attendance.objects.filter(employee=user, date=date, company=company).first()
        attendance_list.append(attendance_obj)

    attendance_dict = {
        'user': user,
        'attendance': attendance_list
    }
    attendance.append(attendance_dict)

    end_of_month = start.end_of('month').day
    context = {'users': users, 'attendance_list': attendance, 'end_of_month': end_of_month}
    return render(request, template_name, context)

    # count = 0
    # date = datetime.date.replace(start.date(), day=1, month=month, year=year, )
    # end = pendulum.date(day=1, month=month, year=year).end_of('month')
    # attendance = []
    # first_attendance = Attendance.objects.filter(employee=user, company=company).first()
    # if first_attendance is None:
    #     context = {'users': users, 'attendance_list': attendance}
    #     return render(request, template_name, context)
    # if first_attendance.date <= end:
    #     if date == start:
    #         end = datetime.date.today()
    #     date_list = []
    #     while date < end:
    #         count += 1
    #         date = date.replace(day=count)
    #         date_list.append(date)
    #     attendance_list = []
    #     for date in date_list:
    #         attendance_obj = Attendance.objects.filter(employee=user, date=date, company=company).first()
    #         attendance_list.append(attendance_obj)
    #     attendance_dict = {
    #         'user': user,
    #         'attendance': attendance_list
    #     }
    #     attendance.append(attendance_dict)
    # end_of_month = pendulum.now().end_of('month').day
    # context = {'users': users, 'attendance_list': attendance}
    # return render(request, template_name, context)


@require_user_access_rights(['owner', 'attendance_policies'])
@login_required
def attendancePolicies(request):
    company = get_company_object_from_user(request.user.id)
    attendance_policies = AttendancePolicy.objects.filter(company=company)
    context = {'attendance_policies': attendance_policies}
    return render(request, 'attendance-policies.html', context)


@require_user_access_rights(['owner', 'attendance_policies'])
@login_required
def deleteAttendancePolicy(request, pk):
    company = get_company_object_from_user(request.user.id)
    attendance_policy = None
    if AttendancePolicy.objects.filter(id=pk, company=company).exists():
        attendance_policy = AttendancePolicy.objects.get(id=pk, company=company)
    if attendance_policy is not None:
        try:
            attendance_policy.delete()
            messages.success(request, 'Attendance Policy has been Deleted')
        except ProtectedError as e:
            messages.error(request,
                           attendance_policy.name + " Policy is  Assigned To Some Users. Unable to Delete This Attendance Policy.")
    return redirect('attendance_policies')


@require_user_access_rights(['owner', 'attendance_policies'])
@login_required
def editAttendancePolicyStatus(request, pk, status):
    company = get_company_object_from_user(request.user.id)
    policy = AttendancePolicy.objects.get(id=pk, company=company)
    state = 'Inactive'
    if status == 'True':
        state = 'Active'
    if policy.policy_status == True and state == 'Active':
        messages.success(request, policy.name + ' Policy is already ' + state)
        return redirect('attendance_policies')
    elif policy.policy_status == False and state == 'Inactive':
        messages.success(request, policy.name + ' Policy is already ' + state)
        return redirect('attendance_policies')
    elif status == 'True':
        policy.policy_status = True
    elif status == 'False':
        policy.policy_status = False
    policy.save()
    messages.success(request, policy.name + ' Policy status updated to  ' + state)
    return redirect('attendance_policies')


@require_user_access_rights(['owner', 'attendance_policies'])
@login_required
def editAttendancePolicy(request, *args, **kwargs):
    company = get_company_object_from_user(request.user.id)
    attendance_policy = get_object_or_404_template_default(AttendancePolicy, id=kwargs.get('pk'), company=company)
    form = AttendancePolicyForm(request, instance=attendance_policy)
    if request.POST:
        form = AttendancePolicyForm(request, request.POST, instance=attendance_policy)
        if form.is_valid():
            form.save()
            messages.success(request, attendance_policy.name + ' Attendance Policy has been updated')
            return redirect(reverse('attendance_policies'))
        else:
            return render(request, 'editAttendance-setting.html',
                          {'form': form, 'attendance_policy_id': attendance_policy.id})
    return render(request, 'editAttendance-setting.html', {'form': form, 'attendance_policy_id': attendance_policy.id})


class ShiftView(LoginRequiredMixin, AttendancePoliciesRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        template_name = 'shifts.html'
        shifts = Shift.objects.filter(company=get_company_object_from_user(request.user.id))
        form_class = ShiftForm()
        context = {'form': form_class, 'shifts': shifts}
        return render(request, template_name, context)

    def post(self, request, *args, **kwargs):
        shift_form = ShiftForm(request.POST)
        if shift_form.is_valid():
            shift = shift_form.save(commit=False)
            shift.company = get_company_object_from_user(request.user.id)
            shift.save()
            messages.success(request, shift.name + ' Shift is added succcessfully')
            return redirect('shift')
        else:
            print(shift_form.errors)
            messages.error(request, 'Form has errors')
            return redirect('shift')


@require_user_access_rights(['owner', 'attendance_policies'])
@login_required
def deleteShift(request, pk):
    shift = None
    company = get_company_object_from_user(request.user.id)
    if Shift.objects.filter(company=company, id=pk).exists():
        shift = Shift.objects.get(company=company, id=pk)
    if shift is not None:
        try:
            shift.delete()
            messages.success(request, 'Shift has been deleted')
        except ProtectedError as e:
            messages.error(request, shift.name + " Shift is  Assigned To Some Attendance Policy. Can't Delete This Shift.")
    return redirect('shift')


@require_user_access_rights(['owner', 'attendance_policies'])
@login_required
def edit_shift_form(request, *args, **kwargs):
    company = get_company_object_from_user(request.user.id)
    shift = get_object_or_404_template_default(Shift, id=kwargs.get('pk'), company=company)
    if request.method == 'POST':
        form = ShiftForm(request.POST, instance=shift)
        if form.is_valid():
            form.save()
            messages.success(request, shift.name + ' Shift Update Successfully')
            return redirect('shift')
        else:
            messages.error(request, 'Shift Not Updated!')
            print(form.errors)
            return redirect('shift')

    if request.is_ajax and request.method == 'GET':
        form = ShiftForm(instance=shift)
        form_string = render_to_string('editShiftForm.html', {'form': form, 'shift_id': shift.id}, request)
        return JsonResponse({'shift_edit_form': form_string}, status=200)

    messages.error(request, 'Processing Error!. Try Again')
    return redirect('projects')


def getWeekdaysNumber(start, end):
    numberOfDays = (end - start).days + 1
    numberOfWeeks = numberOfDays // 7
    reminderDays = numberOfDays % 7
    numberOfDays -= numberOfWeeks * 2
    if reminderDays:
        # this line is creating a set of weekdays for remainder days where 7 and 0 will be Saturday, 6 and -1 will be Sunday
        weekdays = set(range(end.isoweekday(), end.isoweekday() - reminderDays, -1))
        numberOfDays -= len(weekdays.intersection([7, 6, 0, -1]))
    return numberOfDays

# From following functionality employee can request punch in or punch out time.
# def edit_attendacne_punch(request, pk):
#     company = get_company_object_from_user(request.user.id)
#     if request.method == 'POST':
#         punch_type = request.POST['punch_type']
#         punch_time = request.POST['punch_time']
#         time_obj = None
#         if punch_time:
#             now = datetime.datetime.now()
#             user_current_timezone = pytz.timezone(str(timezone.get_current_timezone()))
#             t = datetime.datetime.strptime(punch_time, '%H:%M').time()
#
#             # Convert Timezone aware time to UTC time for saving in database
#             n = now.replace(hour=t.hour, minute=t.minute, second=t.second, microsecond=t.microsecond)
#             locat_dt = user_current_timezone.localize(n)
#             time_obj = locat_dt.astimezone(pytz.utc).time()
#
#             # Testing Convert UTC time to user Timezone time
#             # n2 = now.replace(hour=time_obj.hour, minute=time_obj.minute, second=time_obj.second, microsecond=time_obj.microsecond, tzinfo=pytz.utc)
#             # time_obj2 = n2.astimezone(user_current_timezone).time()
#
#         if punch_type and time_obj:
#             attendance = Attendance.objects.filter(pk=pk, employee=request.user, company=company).first()
#             AttendancePunchRequest.objects.create(attendance=attendance, company=company, punch_time=time_obj,
#                                                   punch_type=punch_type)
#             messages.success(request, 'Punch Request Generated')
#         else:
#             messages.success(request, 'Please Fill Form Correctly and Try Again')
#     return redirect('attendance')
#
#
# @require_user_access_rights(['owner', 'attendance_requests'])
# @login_required
# def attendance_request_admin_view(request, pk):
#     pass
