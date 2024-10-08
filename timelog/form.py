import datetime

from django.db.models import Q
from django.forms import models, ModelForm
from django import forms
from accounts.models import User, Company
from project.models import Project
from timelog.models import TimeLog, ManualTaskName


# class DateTimeInput(forms.TimeInput):
#     input_type = 'time'


class AddTimeLog(models.ModelForm):
    class Meta:
        model = TimeLog
        fields = ('date', 'comments')
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'date', 'value': datetime.datetime.now().date()}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['date'].label = 'Date'
            self.fields['date'].initial = datetime.datetime.now().date()
            self.fields['comments'].widget.attrs.update({
                'required': True
            })

        # def __init__(self, *args, **kwargs):
        #     if 'uuid' in kwargs:
        #         uuid = kwargs.pop('uuid')
        #         user = User.objects.filter(id=uuid).first()
        #     else:
        #         user = None
        #     super().__init__(*args, **kwargs)
        #     # access object through self.instance...
        #     if user:
        #         self.fields['task'].queryset = TimeLog.objects.filter(task__assign_to=user)


class TimeLogForm(forms.ModelForm):
    class Meta:
        model = TimeLog
        fields = ('start_time', 'comments', 'date', 'task', 'project')

        widgets = {
            'date': forms.DateInput(format='%m/%d/%Y', attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company')
        user = kwargs.pop('request_user')
        projects_all = Project.objects.filter(company=company)
        super().__init__(*args, **kwargs)
        self.fields['project'].queryset = projects_all.filter(Q(team=user) | Q(lead_by=user)).distinct()
        self.fields['start_time'].widget = forms.TimeInput()
        self.fields['comments'].widget = forms.Textarea()


class TimeLogManualForm(forms.ModelForm):
    class Meta:
        model = TimeLog
        fields = ('start_time', 'comments', 'date', 'manual_task')

        widgets = {
            'date': forms.DateInput(format='%m/%d/%Y', attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].widget = forms.TimeInput()
        self.fields['comments'].widget = forms.Textarea()


class ManualTaskNameForm(forms.ModelForm):
    class Meta:
        model = ManualTaskName
        fields = ('name',)