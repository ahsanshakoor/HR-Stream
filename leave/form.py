import datetime

from django.forms import models
from django import forms

# from accounts.models import User
from leave.models import LeavePolicy, Leave, Holiday, LeaveRequest

from django.contrib.auth import get_user_model

User = get_user_model()


class DateTimeInput(forms.DateInput):
    input_type = 'date'


class LeavePolicyForm(models.ModelForm):
    class Meta:
        model = LeavePolicy
        fields = ('name', 'description', 'cycle_start_date', 'cycle_end_date', 'is_active',)
        widgets = {
            'cycle_start_date': DateTimeInput(attrs={
                'class': 'form-control'}),
            'cycle_end_date': DateTimeInput(attrs={
                'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Add Leave Policy Name Here'})
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Add Leave Policy Description Here', 'rows': '5', 'cols': '5'})
    # def __init__(self,*args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['name'].label = 'Policy Name'
    #     self.fields['description'].label = 'Policy Description'
    #     self.fields['cycle_type'].label = 'Cycle Type'
    #     self.fields['cycle_start_date'].label = 'Cycle Start Date'
    #     self.fields['working_hour'].label = 'Working Hour'
    #     self.fields['name'].widget.attrs.update({'class':  'form-control col-sm-3 col-md-2', 'placeholder':'Add Policy Name Here'})
    #     self.fields['description'].widget.attrs.update({'class': 'form-control col-sm-3 col-md-2', 'placeholder': 'Add Description Here'})
    #     # self.fields['working_hour'].widget.attrs.update({'class': 'form-control col-sm-3 col-md-2', 'placeholder': 'Working Hour'})
    #     self.fields['cycle_type'].widget.attrs.update({'class': 'form-control col-sm-3 col-md-2'})


class LeaveForm(models.ModelForm):
    class Meta:
        model = Leave
        fields = ('name', 'days', 'is_carry_forward', 'is_active', 'leave_policy',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['leave_policy'].widget.attrs.update(
            {'class': 'form-control', 'hidden': True})


class LeaveRequestForm(models.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ('leave_from', 'leave_to', 'leave_type', 'requested_days', 'reason')
        widgets = {
            'leave_from': forms.DateTimeInput(attrs={'type': 'date', 'value': datetime.datetime.now().date()}),

            'leave_to': forms.DateTimeInput(attrs={'type': 'date', 'value': datetime.datetime.now().date()}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['requested_days'].widget.attrs.update(
            {'class': 'form-control', 'readonly': True, 'required': True})
        self.fields['leave_type'].queryset = self.initial.get('leave_type')
        # self.fields['leave_type'].queryset = Leave.objects.filter(leave_policy=self.instance.leave_policy)


class EditLeaveRequestForm(models.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ('leave_from', 'leave_to', 'leave_type', 'requested_days', 'reason')
        widgets = {
            'leave_from': forms.DateTimeInput(format='%m /%d /%Y '),

            'leave_to': forms.DateTimeInput(format='%m/%d/%Y'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['requested_days'].widget.attrs.update(
            {'class': 'form-control', 'readonly': True, 'required': True})
        # self.fields['leave_type'].queryset = self.initial.get('leave_type')
        # self.fields['leave_from'].queryset = self.initial.get('leave_from')
        # self.fields['leave_to'].queryset = self.initial.get('leave_to')


class LeaveRequestSearchForm(models.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ('leave_from', 'leave_to', 'leave_type', 'employee', 'status')



class HolidayForm(forms.ModelForm):

    class Meta:
        model = Holiday
        fields = ('name', 'date' )
        widgets = {
            'date': DateTimeInput(attrs={
                'class': 'form-control col-sm-3 col-md-2'

            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = 'Holiday Name'
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control col-sm-3 col-md-2', 'placeholder': 'Add Holiday Name Here'})


class DaysForm(forms.Form):
    OPTIONS = (
        ("MONDAY", "MONDAY"),
        ("TUESDAY", "THURSDAY"),
        ("WEDNESDAY", "WEDNESDAY"),
        ("THURSDAY", "THURSDAY"),
        ("FRIDAY", "FRIDAY"),
        ("SATURDAY", "SATURDAY"),
        ("SUNDAY", "SUNDAY"),
    )
    working_days = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=OPTIONS)


# class UserListForm(forms.Form):
    # users = User.objects.all()
    # OPTIONS = []
    # for user in users:
    #     OPTIONS.append((user.first_name, user))
    # users_list = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=OPTIONS)
