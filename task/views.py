from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
# from djqscsv import render_to_csv_response
from import_export import resources

from accounts.utils import get_company_object_from_user
from checkin.models import CheckIn
from home.views import baseelements
from .filter import TaskFilter
from .models import Task
from task.form import addTaskForm, updateTaskForm
from accounts.models import User


class TaskView(LoginRequiredMixin, View):

    form_class = addTaskForm
    # form_class_filter = TaskFilter
    template_name = 'task.html'

    def get(self, request):
        # print('hello')
        company = get_company_object_from_user(request.user.id)
        users = company.users.values_list('id', flat=True)
        user_task = User.objects.filter(id__in=users, report_to=request.user.id)
        # print(users)
        if request.GET.get('search'):
            task_list = Task.objects.filter(assign_to__in=user_task)
            task_filter = TaskFilter(request, request.GET, queryset=task_list)
            homeelement = baseelements(request)
            context1 = {'filter': task_filter}
            context = {**homeelement, **context1}
            return render(request, 'filter_list.html', context)
        if request.GET.get('model_name'):
            if request.GET.get('column_names') == 'All Column':
                task_list = Task.objects.filter(assign_to__in=user_task)
            else:
                column = request.GET.get('column_names')
                task_list = Task.objects.filter(assign_to__in=user_task).values(column)
            task_filter = TaskFilter(request, request.GET, queryset=task_list)
            data = ExportData().export(task_filter.qs)
            response = HttpResponse(data, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=TaskDetails.csv'
            return response
            # return render_to_csv_response(task_filter)

        # status = CheckIn.objects.filter(name=self.request.user).last()
        # form = self.form_class

        current_user = User.objects.filter(id=request.user.id)
        form1 = TaskFilter(request)
        print(form1.form)
        user_tasks = Task.objects.filter(assign_to=request.user.id)
        # count = Task.objects.filter(status=Task.START, assign_to=request.user.id).count()
        homeelement = baseelements(request)
        context1 = {'form1': form1, 'user_tasks': user_tasks}
        context = {**homeelement, **context1}

        return render(request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        form = addTaskForm(request, request.POST, request.FILES)
        print("we are in post")
        print(form)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            print("form is saved")
            return redirect(reverse('task'))
        else:
            print("the form is not valid")
            context = baseelements(request)
            return render(request, 'task.html', context)


class DeleteTask(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if kwargs.get('pk'):
            Task.objects.get(id=kwargs.get('pk')).delete()
            return redirect(reverse('task'))


class UpdateTask(LoginRequiredMixin, View):

    form_class = updateTaskForm

    def get(self, request, *args, **kwargs):
        if request.method == 'GET':
            if kwargs.get('pk'):
                obj = Task.objects.get(id=kwargs.get('pk'))
                form = updateTaskForm(request, instance=obj)
                return render(request, 'updateTask.html', {'form': form })

    def post(self, request, *args, **kwargs):
        print("i am in post")
        if kwargs.get('pk'):
            print("print has a primary key")
            obj = Task.objects.get(id=kwargs.get('pk'))
            form = self.form_class(request, request.POST, request.FILES, instance=obj)
            if form.is_valid():
                task = form.save(commit=False)
                task.save()
                return redirect(reverse('task'))
            else:
                return render(request, 'updateTask.html', {'form': form, })


class ExportData(resources.ModelResource):

    class Meta:
        model = Task


class SingleTask(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        singletask = Task.objects.get(id=kwargs.get('pk'))
        homeelement = baseelements( request)
        context1 = {'singletask': singletask}
        context = {**context1, **homeelement}
        return render(request, 'taskDetails.html', context)


class SingleTaskUpdate(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        singletask = Task.objects.get(id=kwargs.get('pk'))
        if singletask.status != Task.IN_PROGRESS:
            singletask.status = Task.IN_PROGRESS
        else:
            singletask.status = Task.FINISHED
        singletask.save()
        context1 = {'singletask': singletask}
        homeelement = baseelements( request)
        context = {**context1, **homeelement}
        return render(request, 'taskDetails.html', context)


def start_task(request, *args, **kwargs):

    singletask = Task.objects.get(id=kwargs.get('pk'))
    singletask.status = Task.IN_PROGRESS
    singletask.save()
    context1 = {'singletask': singletask}
    homeelement = baseelements(request)
    context = {**context1, **homeelement}
    return render(request, 'taskDetails.html', context)