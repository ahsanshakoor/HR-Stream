import django_filters
from django.forms import models
from django import forms
from accounts.models import User
from task.models import Task


class DateInput(forms.DateInput):
    input_type = 'date'


class addTaskForm(models.ModelForm):

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'priority', 'assign_to', 'due_date', 'file')
        widgets = {
            'due_date': DateInput(),
            'description': forms.Textarea(attrs={'placeholder': 'Add description Here', 'box-sizing': 'border-box;', 'resize': 'none;', 'class': 'form-control col-sm-3 col-md-2'}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assign_to'].label = ''
        self.fields['title'].label = ''
        self.fields['priority'].label = ''
        self.fields['file'].label = ''
        self.fields['description'].label = ''
        self.fields['due_date'].label = ''
        self.fields['assign_to'].queryset = User.objects.filter(report_to=request.user.id)
        self.fields['assign_to'].widget.attrs.update(
            {'class': 'form-control col-sm-3 col-md-2', 'placeholder': "Search by Assignee"})
        self.fields['title'].widget.attrs.update({'class': 'form-control col-sm-3 col-md-2', 'placeholder': "Search by Title"})
        self.fields['file'].widget.attrs.update({'class': 'form-control col-sm-3 col-md-2'})
        self.fields['priority'].widget.attrs.update(
            {'class': 'form-control col-sm-3 col-md-2', 'placeholder': " Search by Priority"})


class updateTaskForm(models.ModelForm):

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'priority', 'assign_to', 'due_date', 'file', 'status')
        widgets = {
            'due_date': DateInput(),
            'description': forms.Textarea(attrs={'placeholder': 'Add description Here', 'box-sizing': 'border-box;', 'resize': 'none;', 'class': 'form-control col-sm-3 col-md-2'}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assign_to'].label = ''
        self.fields['title'].label = ''
        self.fields['status'].label = ''
        self.fields['priority'].label = ''
        self.fields['file'].label = ''
        self.fields['description'].label = ''
        self.fields['due_date'].label = ''
        self.fields['assign_to'].queryset = User.objects.filter(id=request.user.id)
        self.fields['assign_to'].widget.attrs.update(
            {'class': 'form-control col-sm-3 col-md-2', 'placeholder': "Search by Assignee"})
        self.fields['title'].widget.attrs.update({'class': 'form-control col-sm-3 col-md-2', 'placeholder': "Search by Title"})
        self.fields['file'].widget.attrs.update({'class': 'form-control col-sm-3 col-md-2'})
        self.fields['status'].widget.attrs.update({'class': 'form-control col-sm-3 col-md-2', 'placeholder': "Search by Status"})
        self.fields['priority'].widget.attrs.update(
            {'class': 'form-control col-sm-3 col-md-2', 'placeholder': " Search by Priority"})



