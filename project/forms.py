import datetime
from itertools import chain

from django.forms import models, ClearableFileInput, DateTimeInput, inlineformset_factory, Textarea

from accounts.models import User, CompanyClient
from accounts.utils import get_company_object_from_user
from project.models import Project, ProjectFile


class ProjectForm(models.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'start_date', 'end_date', 'priority', 'lead_by', 'team', 'code', 'estimated_time')
        widgets = {
            'start_date': DateTimeInput(attrs={'type': 'date', 'value': datetime.datetime.now().date()}),
            'end_date': DateTimeInput(attrs={'type': 'date', 'value': datetime.datetime.now().date()}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        company = get_company_object_from_user(request.user.id)
        team = User.objects.filter(company=company, report_to=request.user, user_type='employee')
        user = User.objects.filter(id=request.user.id).all()
        for r in request.user.role.all():
            if r.name == 'Owner':
                team = User.objects.filter(company=company, user_type='employee')
        team = team | user
        self.fields['team'].queryset = team
        self.fields['lead_by'].queryset = team
        # self.fields['client'].queryset = CompanyClient.objects.filter(company=company)


class ProjectEditForm(models.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'start_date', 'end_date', 'priority', 'lead_by', 'client', 'team', 'code', 'estimated_time')
        # widgets = {
        #     'start_date': DateTimeInput(attrs={'type': 'date'}),
        #     'end_date': DateTimeInput(attrs={'type': 'date', 'value': datetime.datetime.now().date()}),
        # }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        company = get_company_object_from_user(request.user.id)
        team = User.objects.filter(company=company, report_to=request.user, user_type=User.EMPLOYEE)
        user = User.objects.filter(id=request.user.id)
        for r in request.user.role.all():
            if r.name == 'Owner':
                team = User.objects.filter(company=company, user_type=User.EMPLOYEE)
        team = team | user
        self.fields['team'].queryset = team
        self.fields['lead_by'].queryset = team
        self.fields['client'].queryset = CompanyClient.objects.filter(company=company)


class ProjectFileForm(models.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ('file',)
        widgets = {
            'file': ClearableFileInput(attrs={'multiple': True}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = False


class ProjectFileSetForm(models.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ('file',)
        widgets = {
            'file': ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = False


ProjectFileFormSet = inlineformset_factory(Project, ProjectFile, extra=1, form=ProjectFileSetForm)


