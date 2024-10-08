from django.forms import models, SplitDateTimeWidget, TimeInput, MultipleChoiceField, CheckboxSelectMultiple
from django import forms
from accounts.utils import get_company_object_from_user
from attendance.models import AttendancePolicy, Shift


class AttendancePolicyForm(models.ModelForm):
    class Meta:
        model = AttendancePolicy
        fields = ('name', 'description', 'working_hour_policy', 'grace_time', 'overtime', 'working_hour', 'policy_status', 'shift')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Add Attendance Policy Name Here'})
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Add Attendance Policy Description Here', 'rows': '5', 'cols': '5'})
        self.fields['shift'].queryset=Shift.objects.filter(company=get_company_object_from_user(request.user.id))


class ShiftForm(models.ModelForm):
    OPTIONS = (
        ("MONDAY", "MONDAY"),
        ("TUESDAY", "THURSDAY"),
        ("WEDNESDAY", "WEDNESDAY"),
        ("THURSDAY", "THURSDAY"),
        ("FRIDAY", "FRIDAY"),
        ("SATURDAY", "SATURDAY"),
        ("SUNDAY", "SUNDAY"),
    )
    class Meta:
        model = Shift
        fields = ('name', 'start_time', 'end_time', 'weekdays', 'shift_Allowance',)
        widgets = {
            'start_time': TimeInput(attrs={'class': 'form-control timepicker fa fa-clock-o'}),

            'end_time': TimeInput(attrs={'class': 'form-control timepicker fa fa-clock-o'}),
        }