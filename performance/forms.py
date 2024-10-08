from django import forms
from django.db import models
from django.forms import modelformset_factory

from accounts.forms import User
from performance.models import Performance, Indicator


# class ManualPendingPayrollForm(forms.ModelForm):
#
#     def __init__(self, *args, **kwargs):
#         company = kwargs.pop('company')
#         super().__init__(*args, **kwargs)
#         self.fields['user'].queryset = User.objects.filter(company=company, user_type=User.EMPLOYEE).all()
#         self.fields['indicator'].queryset = Indicator.objects.filter(company=company).all()
#
#     class Meta:
#         model = Performance
#         fields = ('employee', 'date', 'comment', 'indicator')
#         widgets = {
#             'date': forms.DateInput(format='%m/%d/%Y', attrs={'type': 'date'})
#         }
#


class PerformanceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company')
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = User.objects.filter(company=company, user_type=User.EMPLOYEE).all()

    class Meta:
        model = Performance
        fields = ('employee', 'comment', 'date')
        widgets = {
                    'date': forms.DateInput(format='%m/%d/%Y', attrs={'type': 'date'})
                }


class PerformanceIndicatorForm(forms.ModelForm):

    obtained_weightage = forms.IntegerField(initial=0, min_value=0 )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].disabled = True
        self.fields['total_weightage'].disabled = True
        self.fields['obtained_weightage'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Indicator
        fields = ('name', 'total_weightage', 'status')


PerformanceIndicatorFormSet = modelformset_factory(Indicator, form=PerformanceIndicatorForm, extra=0,)


class IndicatorForm(forms.ModelForm):
    class Meta:
        model = Indicator
        fields = ('name', 'total_weightage', 'status')
