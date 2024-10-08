import datetime

from django.forms import models, Textarea, DateTimeInput, ModelForm as forms_modelForm, inlineformset_factory

from accounts.forms import CustomClearableFileInput
from accounts.models import User
from accounts.utils import get_company_object_from_user
from tasks.models import Task, Card, Board, CardFile


class TaskForm(models.ModelForm):

    class Meta:
        model = Task
        fields = ('name', 'project',)
        widgets = {
            'name': Textarea(),
        }


class TaskBoardForm(models.ModelForm):
    class Meta:
        model = Task
        fields = (
            'name', 'description', 'project', 'due_date', 'priority', 'progress', 'assign_to', 'follower'
        )
        widgets = {
            'due_date': DateTimeInput(attrs={'type': 'date', 'value': datetime.datetime.now().date}),
        }


class TaskBoardEditForm(models.ModelForm):
    class Meta:
        model = Task
        fields = (
            'name', 'description', 'project', 'due_date', 'priority', 'progress', 'assign_to', 'follower', 'status'
        )
        # widgets = {
        #     'due_date': DateTimeInput(attrs={'type': 'date', 'value': datetime.datetime.now().date}),
        # }

    def __init__(self, request, *args, **kwargs):
        company = kwargs.pop('company')
        super().__init__(*args, **kwargs)
        self.fields['assign_to'].queryset = User.objects.filter(company=company, user_type=User.EMPLOYEE)
        self.fields['follower'].queryset = User.objects.filter(company=company)


class BoardForm(models.ModelForm):
    class Meta:
        model = Board
        fields = ('name','project',)


class CardForm(models.ModelForm):

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company')
        super().__init__(*args, **kwargs)
        self.fields['assign_to'].queryset = User.objects.filter(company=company, user_type=User.EMPLOYEE)
        self.fields['follower'].queryset = User.objects.filter(company=company)

    class Meta:
        model = Card
        fields = (
            'name', 'description', 'due_date', 'priority', 'progress', 'assign_to', 'follower', 'board', 'status'
        )
        widgets = {
            'due_date': DateTimeInput(format=('%Y-%m-%d'), attrs={'type': 'date', 'value': datetime.datetime.now().date}),
        }


class addTaskForm(models.ModelForm):
    class Meta:
        model = Task
        fields = (
            'name', 'description', 'due_date', 'priority', 'progress', 'assign_to', 'follower', 'project'
        )
        widgets = {
            'due_date': DateTimeInput(attrs={'type': 'date', 'value': datetime.datetime.now().date}),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        company = get_company_object_from_user(request.user.id)
        self.fields['assign_to'].queryset = User.objects.filter(company=company, user_type=User.EMPLOYEE)
        self.fields['follower'].queryset = User.objects.filter(company=company)


class CardFileForm(forms_modelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget = CustomClearableFileInput()

    class Meta:
        model = CardFile
        fields = ('file',)


CardFileFormSet = inlineformset_factory(Card, CardFile, form=CardFileForm, extra=1, can_delete=True)