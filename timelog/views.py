from datetime import datetime
import datetime as datetime
import pendulum as pendulum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import View
from import_export import resources

from accounts.decorators import require_user_access_rights
from accounts.mixins import TimeLogRequiredMixin
from accounts.models import User
from accounts.utils import get_company_object_from_user, get_object_or_404_template_default
from checkin.views import total_hours
from home.views import baseelements
from project.models import Project
from tasks.models import Task, Card, Board
from timelog.filter import TimeLogFilter
from timelog.form import AddTimeLog, TimeLogForm, TimeLogManualForm, ManualTaskNameForm
from timelog.models import TimeLog, ManualTaskName
from django.utils import timezone


class TimeLogView(LoginRequiredMixin, View):
    form_class = AddTimeLog
    form_class_second = TimeLogFilter
    template_name = 'time-log-calender.html'

    def get(self, request, *args, **kwargs):
        company = get_company_object_from_user(request.user.id)
        users = User.objects.filter(company=company).values_list('id', flat=True)
        projects_all = Project.objects.filter(company=company)
        projects = projects_all.filter(Q(team=request.user) | Q(lead_by=request.user)).distinct()
        timeLogForm = TimeLogForm(company=company, request_user=request.user)
        timeLogManualForm = TimeLogManualForm()
        context = {'projects': projects, 'timeLogForm': timeLogForm, 'timeLogManualForm': timeLogManualForm}
        if kwargs.get('table') == 'table':
            timeLogs = TimeLog.objects.filter(company=company, name=request.user).order_by('date').select_related('name')
            context = {'projects': projects, 'timeLogForm': timeLogForm, 'timeLogs': timeLogs, 'timeLogManualForm': timeLogManualForm}
            return render(request, 'time-log-table.html', context)
        return render(request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):

        company = get_company_object_from_user(request.user.id)
        user = User.objects.filter(id=request.user.id, company=company).first()
        timeLogForm = TimeLogForm(request.POST, company=company, request_user=request.user)
        if timeLogForm.is_valid():
            timeLog = timeLogForm.save(commit=False)
            timeLog.name = user
            timeLog.company = company
            timeLog.save()
            messages.info(request, 'Time Log has been saved')
            return redirect('time_log')
        else:
            messages.error(request, 'An error is occurred while saving Time Log. Please save again')
            timeLogForm = TimeLogForm(company=company, request_user=request.user)
            context = {'timeLogForm': timeLogForm}
            return render(request, template_name=self.template_name, context=context)


@require_user_access_rights(['owner', 'basic'])
@login_required
def manual_time_log(request, *args, **kwargs):
    company = get_company_object_from_user(request.user.id)
    user = User.objects.filter(id=request.user.id, company=company).first()
    timeLogForm = TimeLogManualForm(request.POST)
    table = 'table'
    if timeLogForm.is_valid():
        timeLog = timeLogForm.save(commit=False)
        timeLog.name = user
        timeLog.company = company
        timeLog.save()
        messages.info(request, 'Time Log has been saved')
        if kwargs.get('table'):
            return redirect('time_log', kwargs)
        return redirect('time_log')
    else:
        messages.error(request, 'An error is occurred while saving Time Log. Please save again')
        if kwargs.get('table'):
            return redirect('time_log', kwargs)
        return redirect('time_log')


@require_user_access_rights(['owner', 'basic'])
@login_required
def get_time_log_calender(request):
    if request.is_ajax:
            company = get_company_object_from_user(request.user.id)
            timelogs = TimeLog.objects.filter(company=company, name=request.user)
            event_list = []
            for timelog in timelogs:
                dict = {}
                dict['id'] = timelog.id
                if timelog.task:
                    dict['title'] = timelog.task.name
                elif timelog.manual_task:
                    dict['title'] = timelog.manual_task.name
                dict['start'] = timelog.date
                dict['time'] = timelog.start_time
                if timelog.submit_status == 'SAVED':
                    dict['className'] = 'bg-primary'
                elif timelog.submit_status == 'SUBMITTED':
                    dict['className'] = 'bg-primary2'
                event_list.append(dict)
            return JsonResponse({'events': event_list}, status=200)

    return JsonResponse({'error': ''}, status=400)


@require_user_access_rights(['owner', 'basic'])
@login_required
def update_time_log(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        start_time = request.POST.get('start_time')
        submit_status = request.POST.get('submit_status')
        if start_time == '':
            messages.error(request, 'Time can not be empty')
            JsonResponse({'error': 'Time can not be empty'}, status=400)
        start_time = timezone.datetime.strptime(start_time, '%H:%M:%S').time()
        timeLog = TimeLog.objects.get(id=id)
        if submit_status == 'SUBMITTED':
            timeLog.submit_status = TimeLog.SUBMITTED
        timeLog.start_time = start_time
        timeLog.save()
        return JsonResponse({'success': 'Time Log Updated' }, status=200)


def approve(request, *args, **kwargs):
    obj = TimeLog.objects.get(pk=kwargs.get('pk'))
    obj.status = TimeLog.APPROVED
    obj.save()
    return timelogDetails(request)


def reject(request, *args, **kwargs):
    obj = TimeLog.objects.get(pk=kwargs.get('pk'))
    obj.status = TimeLog.REJECTED
    obj.save()
    return timelogDetails(request)


@require_user_access_rights(['owner', 'timelog'])
@login_required
def timelogDetails(request, *args, **kwargs):
    # company = get_company_object_from_user(request.user.id)
    # users = company.users.values_list('id', flat=True)
    users = User.objects.filter(report_to=request.user.id)
    approved = TimeLog.objects.filter(status=TimeLog.APPROVED, name__in=users)
    rejected = TimeLog.objects.filter(status=TimeLog.REJECTED, name__in=users)
    pending = TimeLog.objects.filter(status=TimeLog.PENDING, name__in=users)
    today = pendulum.now().date()
    start = today.start_of('week')
    end = today.end_of('week')
    form = TimeLogFilter(request)
    form1 = TimeLogFilter(request)
    homeelement = baseelements(request)
    if request.GET.get('search'):
        timelog_list = TimeLog.objects.filter(name__in=users)
        timelog_filter = TimeLogFilter(request.GET, queryset=timelog_list,)
        context1 = {'approved': approved, 'rejected': rejected, 'pending': pending, 'weekend': end, 'weekstart': start,
                    'form': form, 'form1': form1, 'timelog_filter': timelog_filter}
        context = {**context1, **homeelement}
        return render(request, template_name='time_logDetails.html', context=context)
    context1 = {'approved': approved, 'rejected': rejected, 'pending': pending,'weekend': end, 'weekstart': start, 'form': form, 'form1': form1}
    context = {**context1, **homeelement}
    return render(request, template_name='time_logDetails.html', context=context)


class TimeLogAdmin(LoginRequiredMixin, TimeLogRequiredMixin, View):
    template_name = 'time_log_admin.html'

    def get(self, request, *args, **kwargs):

        company = get_company_object_from_user(request.user.id)
        user = User.objects.get(id=request.user.id, company=company)
        users =User.objects.filter(company=company, report_to=user)
        timelogs = TimeLog.objects.filter(company=company, name__in=users)
        total_hours = None
        context = {'users':users, 'timelogs': timelogs, 'total_hours': total_hours}
        return render(request, template_name=self.template_name,context=context)

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        company = get_company_object_from_user(request.user.id)
        user = User.objects.get(id=user_id, company=company)
        users = User.objects.filter(company=company)  # , report_to=user
        timelogs = TimeLog.objects.filter(company=company, name=user, date__gte=start_date, date__lte=end_date).order_by('date')
        total_hours = 0
        start = None
        end = None
        if timelogs is not None:
            total_hours = timelogs.aggregate(Sum('start_time'))['start_time__sum']
            if total_hours is not None:
                total_hours = total_hours.total_seconds()
                h = total_hours // 3600
                m = (total_hours % 3600) // 60
                total_hours = "%d:%d" % (h, m)
                start = timelogs.first().date
                end = timelogs.last().date
        context = {'users': users, 'timelogs': timelogs, 'total_hours': total_hours, 'start_date_approval': start, 'end_date_approval': end}
        return render(request, template_name=self.template_name, context=context)


def approve_time_log(request):
    start = datetime.datetime.strptime(request.POST.get('start_date_approval'), "%b. %d, %Y").strftime('%Y-%m-%d')
    end = datetime.datetime.strptime(request.POST.get('end_date_approval'), "%b. %d, %Y").strftime('%Y-%m-%d')
    company = get_company_object_from_user(request.user.id)
    timelogs = TimeLog.objects.filter(company=company, date__gte=start, date__lte=end)
    for timelog in timelogs:
        timelog.status = TimeLog.APPROVED
        timelog.save()
    return redirect('time_log_details')


@require_user_access_rights(['owner', 'basic'])
@login_required
def get_task(request, pro_id=None):
    if request.is_ajax:
        if pro_id is not None:
            company = get_company_object_from_user(request.user.id)
            board = Board.objects.filter(project=pro_id, company=company)
            tasks = list(
                Card.objects.filter(board__in=board, company=company).values_list('id', 'name'))
            return JsonResponse({'tasks': tasks}, status=200)

    return JsonResponse({'error': ''}, status=400)


def singleTimeLog(request, *args, **kwargs):
    obj = TimeLog.objects.get(pk=kwargs.get('pk'))
    homeelement = baseelements(request)
    end = datetime.datetime.combine(datetime.datetime.today(), obj.end_time)
    start = datetime.datetime.combine(datetime.datetime.today(), obj.start_time)
    hours = total_hours(end , start )
    context1 = {'timelog': obj, 'hours': hours}
    context = {**context1, **homeelement}
    return render(request, template_name='singleTimeLog.html', context=context)


class ExportData(resources.ModelResource):

    class Meta:
        model = TimeLog


class DeleteTimeLog(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            TimeLog.objects.get(id=kwargs.get('pk')).delete()
            return JsonResponse({'tasks': 'Time Log Deleted'}, status=200)


@require_user_access_rights(['owner', 'basic'])
@login_required
def delete_time_log_table(request, *args, **kwargs):
    try:
        if kwargs.get('pk'):
            TimeLog.objects.get(id=kwargs.get('pk')).delete()
            messages.success(request, 'Time Log Deleted')
            return redirect('time_log_table', kwargs.get('table'))
    except:
        messages.error(request, 'Already Deleted')
        return redirect('time_log_table', kwargs.get('table'))


@require_user_access_rights(['owner', 'basic'])
@login_required
def edit_timeLog_table(request, time_id=None):
    if request.is_ajax and request.method == 'GET':
        timelog = get_object_or_404_template_default(TimeLog, id=time_id)
        dict = {}
        dict['id'] = timelog.id
        if timelog.task:
            dict['title'] = timelog.task.name
        elif timelog.manual_task:
            dict['title'] = timelog.manual_task.name
        dict['time'] = timelog.start_time
        dict['submit_status'] = timelog.submit_status
        form_string = render_to_string('time-log-edit-form.html', {'timelog': dict}, request)
        return JsonResponse({'timeLog_form': form_string}, status=200)
    else:
        return JsonResponse({'error': 'can not edit'}, status=400)


@require_user_access_rights(['owner', 'timelog'])
@login_required
def timelog_status(request, timelog_id, name):
    company = get_company_object_from_user(request.user.id)
    table = 'table'
    try:
        timelog = TimeLog.objects.get(id=timelog_id, company=company)
        if timelog.status == name:
            messages.success(request, 'Status already set to ' + name)
        else:
            timelog.status = name
            messages.success(request, 'Status is updated to ' + name)
            timelog.save()
        return redirect('time_log_details')
    except:
        messages.warning(request, 'Time Log is deleted by employee')
        return redirect('time_log_details')


@login_required
def company_manual_task_name(request):
    company = get_company_object_from_user(request.user.id)
    manual_task_names = ManualTaskName.objects.filter(company=company).all()
    return render(request, 'manual-task-name.html', {'manual_task_names': manual_task_names})


@login_required
def create_n_edit_manual_task_name(request, manual_task_name_id=None):

    if request.method == "POST":
        manual_task_name_name = request.POST['name'].strip()
        if manual_task_name_name not in (None, ''):
            if manual_task_name_id:
                manual_task_name = get_object_or_404_template_default(ManualTaskName, id=manual_task_name_id)
                manual_task_name.name = manual_task_name_name
                manual_task_name.save()
                messages.success(request, 'Manual Task Name Update Successful!')
            else:
                manual_task_name = ManualTaskName.objects.create(name=manual_task_name_name,
                                                      company=get_company_object_from_user(request.user.id))
                manual_task_name.save()
                messages.success(request, 'Manual Task Name Addition Successful!')
        else:
            messages.error(request, 'Manual Task Name name is empty')
    if request.is_ajax and request.method == 'GET':
        manual_task_name = get_object_or_404_template_default(ManualTaskName, id=manual_task_name_id)
        form = ManualTaskNameForm(instance=manual_task_name)
        form_string = render_to_string('manual_task_name_form.html', {'form': form, 'manual_task_name': manual_task_name}, request)
        return JsonResponse({'manual_task_name_form': form_string}, status=200)
    return redirect('showManualTaskName')


# working

@login_required
def delete_manual_task_name(request, manual_task_name_id=None):
    if manual_task_name_id is not None:
        try:
            manual_task_name = get_object_or_404_template_default(ManualTaskName, id=manual_task_name_id)
            manual_task_name.delete()
        except ProtectedError:
            m = 'Deleting {0} will also delete its designations. Please make sure that all designations under {0} are not assigned to any employee.'.format(
                manual_task_name.name)
            messages.error(request, m)
            return redirect('showManualTaskName')

        messages.success(request, 'ManualTaskName Deleted Successful!')
    return redirect('showManualTaskName')


@require_user_access_rights(['owner', 'basic'])
@login_required
def update_time_log(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        start_time = request.POST.get('start_time')
        submit_status = request.POST.get('submit_status')
        if start_time == '':
            messages.error(request, 'Time can not be empty')
            JsonResponse({'error': 'Time can not be empty'}, status=400)
        start_time = timezone.datetime.strptime(start_time, '%H:%M:%S').time()
        timeLog = TimeLog.objects.get(id=id)
        if submit_status == 'SUBMITTED':
            timeLog.submit_status = TimeLog.SUBMITTED
        timeLog.start_time = start_time
        timeLog.save()
        return JsonResponse({'start_time': timelog.start_time, 'success': 'Time Log Updated' }, status=200)

