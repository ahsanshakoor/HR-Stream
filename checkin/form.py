from django.forms import models
from django import forms
from checkin.models import CheckIn


class DateTimeInput(forms.DateInput):
    input_type = 'date'


class CheckInForm(models.ModelForm):
    class Meta:
        model = CheckIn
        fields = ('checkin', 'comment')

        widgets = {
            'checkin': DateTimeInput(attrs={
                'class': 'form-control datetimepicker-input',
                'data-target': '#datetimepicker1'
                    })
        }
