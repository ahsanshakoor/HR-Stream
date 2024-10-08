from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from accounts.decorators import require_user_access_rights
from accounts.utils import get_company_object_from_user
from .models import Todo
from todo.form import addTodoForm


class Todos(LoginRequiredMixin, View):
    form_class = addTodoForm
    template_name = 'todo.html'

    def get(self, request):
        company = get_company_object_from_user(request.user.id)
        form = self.form_class
        todos = Todo.objects.filter(created_by=request.user, company=company)
        count = Todo.objects.filter(is_read=False).count()
        context = {'form': form, 'todos': todos, 'count': count}
        return render(request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.company = get_company_object_from_user(request.user.id)
            todo.created_by = request.user
            todo.save()
            return redirect(reverse('index'))
        else:
            messages.error(request, '>goal Detail is required')
            return redirect(reverse('index'))


class DeleteTodo(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if Todo.objects.filter(id=kwargs.get('pk')).exists():
            Todo.objects.get(id=kwargs.get('pk')).delete()
        return redirect(reverse('index'))


class UpdateTodo(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):

        obj = Todo.objects.get(id=kwargs.get('pk'))
        if obj.is_read is False:
            obj.is_read = True
            obj.save()
        else:
            obj.is_read = False
            obj.save()
        return redirect('index')


@login_required
def update_todo_list(request, *args, **kwargs):
    obj = Todo.objects.get(id=kwargs.get('pk'))
    if obj.is_read is False:
        obj.is_read = True
        obj.save()
    else:
        obj.is_read = False
        obj.save()
    return redirect('todo')


@login_required
def delete_todo_list(request, *args, **kwargs):
    if Todo.objects.filter(id=kwargs.get('pk')).exists():
        Todo.objects.get(id=kwargs.get('pk')).delete()
    return redirect('todo')


@login_required
def add_todo_list(request, *args, **kwargs):
    form = addTodoForm(request.POST)
    if form.is_valid():
        todo = form.save(commit=False)
        todo.created_by = request.user
        todo.company = get_company_object_from_user(request.user.id)
        todo.save()
        return redirect('todo')