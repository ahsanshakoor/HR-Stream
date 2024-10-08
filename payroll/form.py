from django.forms import models, formset_factory, ClearableFileInput, inlineformset_factory
from django import forms
from accounts.models import User, Company
from payroll.models import PayrollPolicy, PayrollItem, PayrollTaxItem, HealthInsurance, SalaryAdjustment, \
    PendingPayrolls, ClaimType, Claim, ClaimFile


class DateTimeInput(forms.DateInput):
    input_type = 'date'


class PayrollPolicyForm(models.ModelForm):
    class Meta:
        model = PayrollPolicy
        fields = ('name', 'description', 'pay_period_start', 'pay_period_end',
                  'pay_period_start_date', 'pay_period_end_date', 'payroll_cycle')
        widgets = {
            'pay_period_start_date': forms.DateInput(format='%m/%d/%Y', attrs={'type': 'date'}),
            'pay_period_end_date': forms.DateInput(format='%m/%d/%Y', attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Add Payroll Policy Name Here'})
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Add Payroll Description Here', 'rows': '5', 'cols': '5'})


class SalaryAdjustmentForm(forms.Form):
    name = forms.CharField(max_length=150)
    amount = forms.DecimalField(max_digits=10, decimal_places=0)
    adjustment_type = forms.ChoiceField(choices=SalaryAdjustment.TYPE)

    # class Meta:
    #     model = SalaryAdjustment
    #     fields = ('name', 'amount', 'adjustment_type')
        # widgets = {
        #     'payroll': forms.HiddenInput()
        # }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['name'].label = 'Adjustment Name'
    #     self.fields['amount'].label = 'Amount'
    #     self.fields['adjustment_type'].label = 'Adjustment Type'
    #     self.fields['name'].widget.attrs.update(
    #         {'placeholder': 'Add Name Here',  'required': True})
    #     self.fields['amount'].widget.attrs.update({'required': True})
    #     self.fields['adjustment_type'].widget.attrs.update(
    #         {'required': True})


SalaryAdjustmentFormset = formset_factory(form=SalaryAdjustmentForm)


class PayrollItemForm(models.ModelForm):
    class Meta:
        model = PayrollItem
        fields = ('payroll_policy', 'amount', 'name', 'adjustment_type', 'is_active')


class PayrollTaxItemForm(models.ModelForm):
    class Meta:
        model = PayrollTaxItem
        fields = ('payroll_policy', 'name', 'percentage', 'is_active')


class HealthInsuranceForm(forms.ModelForm):
    class Meta:
        model = HealthInsurance
        fields = ('name', 'description', 'company_amount', 'employee_amount', 'active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Add Health Insurance Name Here'})
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Add Health Insurance Description Here', 'rows': '5', 'cols': '5'})


class ManualPendingPayrollForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company')
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.filter(company=company, user_type=User.EMPLOYEE).all()

    class Meta:
        model = PendingPayrolls
        fields = ('user', 'start_date', 'end_date')
        widgets = {
            'start_date': forms.DateInput(format='%m/%d/%Y', attrs={'type': 'date'}),
            'end_date': forms.DateInput(format='%m/%d/%Y', attrs={'type': 'date'})
        }


class ManualWorkHours(forms.Form):
    hours = forms.IntegerField()


class ClaimTypeForm(forms.ModelForm):
    class Meta:
        model = ClaimType
        fields = ('name',)


class ClaimForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        company_name = kwargs.pop('company_name')
        super().__init__(*args, **kwargs)
        company = Company.objects.filter(name=company_name)
        company = company.first()
        self.fields['claim_type'].queryset = ClaimType.objects.filter(company=company)
        self.fields['date'].widget = forms.DateInput(attrs={'type': 'date'})

    class Meta:
        model = Claim
        fields = ('claim_type', 'date', 'detail', 'amount')


class ClaimFileForm(models.ModelForm):
    class Meta:
        model = ClaimFile
        fields = ('file',)
        widgets = {
            'file': ClearableFileInput(attrs={'multiple': True}),
        }


class ClaimFileSetForm(models.ModelForm):
    class Meta:
        model = ClaimFile
        fields = ('file',)
        widgets = {
            'file': ClearableFileInput(),
        }


ClaimFileFormSet = inlineformset_factory(Claim, ClaimFile, extra=1, form=ClaimFileSetForm)


