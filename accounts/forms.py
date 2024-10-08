import os

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm
from django import forms
from django.forms import inlineformset_factory

from attendance.models import AttendancePolicy
from leave.models import LeavePolicy
from payroll.models import PayrollPolicy
from .models import Company, Designation, Department, UserSalary, PersonalInfo, EmergencyContact, EducationInfo, \
    Experience, BankInfo, CompanyClient, UserFile, Announcement
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()


class UserLoginForm(AuthenticationForm):

    # def confirm_login_allowed(self, user):
    #     if not user.is_active:
    #         raise forms.ValidationError('Please Confirm your email address first.', code='invalid_login')

    def clean_username(self):
        username = self.cleaned_data['username']
        username_existed = User.objects.filter(username=username).first()
        if username:
            if username_existed:
                if username_existed.is_active:
                    return username
                else:
                    raise forms.ValidationError('Please Confirm your email address by visiting your inbox.', code='invalid_login')
            else:
                raise forms.ValidationError('You are not authorized user',
                                            code='invalid_login')
        else:
            raise forms.ValidationError('Enter correct username',code='invalid_login')


class SignupForm(UserCreationForm):
    company_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ('company_name', 'first_name', 'last_name', 'username', 'email', 'password1', 'password2',)

    def clean_company_name(self):
        company_name = self.cleaned_data['company_name']
        company_name_existed = Company.objects.filter(name=company_name).exists()
        if company_name:
            if company_name_existed:
                raise forms.ValidationError('Company Name already exists')
            else:
                return company_name

    def clean_username(self):
        username = self.cleaned_data['username']
        username_existed = User.objects.filter(username=username).first()
        if username:
            from django.core.validators import validate_email
            try:
                validate_email(username)
                raise forms.ValidationError("Username can't be an email")
            except:
                pass

            if username_existed:
                raise forms.ValidationError('Username already exists')
            else:
                return username


class EmailValidationOnForgotPassword(PasswordResetForm):
    # template_name = 'registration/password_rest_form.html'

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['email'].widget.attrs.update(
    #         {'class': 'form-control', 'placeholder': "example@xyz.com", "style": "text-transform: lowercase;"})

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("There is no user registered with this email!")

        return email


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = ''
        self.fields['new_password2'].label = ''
        # self.fields['new_password1'].widget.attrs.update(
        #     {'class': 'form-control', "style": "text-transform: lowercase;", 'placeholder': "New Password"})
        # self.fields['new_password2'].widget.attrs.update(
        #     {'class': 'form-control', "style": "text-transform: lowercase;", 'placeholder': "Confirm Password"})
        self.fields['new_password1'].help_text = None
        self.fields['new_password2'].help_text = None


class UserSalaryForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comments'].widget.attrs.update(
            {'rows': '5', 'cols': '5'})

    class Meta:
        model = UserSalary
        fields = ['salary', 'salary_raise', 'employment_type', 'salary_type', 'comments']


class NewEmployeeSalaryForm(forms.ModelForm):

    class Meta:
        model = UserSalary
        fields = ['salary', 'employment_type', 'salary_type']


class BankInfoForm(forms.ModelForm):

    class Meta:
        model = BankInfo
        fields = ('name', 'address', 'routing', 'account_no', 'account_type', 'account_title')


class NewEmployeeForm(forms.ModelForm):
    role = forms.ModelMultipleChoiceField(queryset=User.objects)
    report_to = forms.ModelChoiceField(queryset=User.objects)

    def __init__(self, *args, **kwargs):
        company_name = kwargs.pop('company_name')
        super().__init__(*args, **kwargs)
        company = Company.objects.filter(name=company_name).prefetch_related('company_roles')
        company = company.first()
        self.fields['role'].queryset = company.company_roles.exclude(name='Owner')
        self.fields['report_to'].queryset = company.users.filter(user_type=User.EMPLOYEE).all()
        self.fields['department'].queryset = Department.objects.filter(company=company).all()
        self.fields['leave_policy'].queryset = LeavePolicy.objects.filter(company=company, is_active=True).all()
        self.fields['payroll_policy'].queryset = PayrollPolicy.objects.filter(company=company).all()
        self.fields['attendance_policy'].queryset = AttendancePolicy.objects.filter(company=company, policy_status=True).all()
        self.fields['user_code'].widget.attrs['readonly'] = True
        self.fields['joining_date'].widget = forms.DateInput(attrs={'type': 'date'})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'department', 'role', 'report_to', 'designation', 'user_code',
                  'joining_date', 'leave_policy', 'payroll_policy', 'attendance_policy')


class NewEmployeeOnBoardingForm(forms.ModelForm):
    set_password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dob'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['profile_pic'].widget = forms.FileInput()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'profile_pic', 'cell', 'gender', 'dob', 'address',
                  'percentage_401k', 'apply_401k_before_tax')

    def clean_confirm_password(self):
        password1 = self.cleaned_data.get('set_password')
        password2 = self.cleaned_data.get('confirm_password')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('The two password fields did not match')
        return password2


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('name',)


class DesignationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company')
        super().__init__(*args, **kwargs)
        departments = Department.objects.filter(company=company) #.prefetch_related('designations')
        self.fields['department'].queryset = departments

    class Meta:
        model = Designation
        fields = '__all__'


class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = ('city', 'state', 'zip_code', 'country')


class ProfileInfoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        company_name = kwargs.pop('company_name')
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].widget = forms.FileInput()
        company = Company.objects.filter(name=company_name).prefetch_related('company_roles', 'users').first()

        self.fields['role'].queryset = company.company_roles.exclude(name='Owner')
        self.fields['report_to'].queryset = company.users.filter(user_type=User.EMPLOYEE).exclude(id=self.instance.id)
        self.fields['department'].queryset = Department.objects.filter(company=company)
        self.fields['designation'].queryset = Designation.objects.filter(company=company)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'profile_pic', 'cell', 'address',
                  'department', 'designation', 'role', 'report_to'
                  )


class ProfileInfoFormWithoutRole(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        company_name = kwargs.pop('company_name')
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].widget = forms.FileInput()
        company = Company.objects.filter(name=company_name).prefetch_related('company_roles', 'users').first()

        self.fields['report_to'].queryset = company.users.filter(user_type=User.EMPLOYEE).exclude(id=self.instance.id)
        self.fields['department'].queryset = Department.objects.filter(company=company)
        self.fields['designation'].queryset = Designation.objects.filter(company=company)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'profile_pic', 'cell', 'address',
                  'department', 'designation', 'report_to'
                  )


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ('name', 'relationship', 'phone')


class EducationInfoForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['starting_date'].widget = forms.DateInput(
            attrs={'type': 'date'}
        )
        self.fields['ending_date'].widget = forms.DateInput(
            attrs={'type': 'date'}
        )

    class Meta:
        model = EducationInfo
        fields = ('institution', 'degree', 'starting_date', 'ending_date')
        # exclude = ()


EducationInfoFormSet = inlineformset_factory(User, EducationInfo, form=EducationInfoForm,
                                             extra=1, can_delete=True)


class ExperienceForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['period_from'].widget = forms.DateInput(
            attrs={'type': 'date'}
        )
        self.fields['period_to'].widget = forms.DateInput(
            attrs={'type': 'date'}
        )

    class Meta:
        model = Experience
        fields = ('company_name', 'job_position', 'period_from', 'period_to')


ExperienceFormSet = inlineformset_factory(User, Experience, form=ExperienceForm,
                                          extra=1, can_delete=True)


class NewClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client_code'].widget.attrs['readonly'] = True
    #     company_name = kwargs.pop('company_name')
    #
    #     company = Company.objects.filter(name=company_name).prefetch_related('company_roles')
    #     company = company.first()
    #     self.fields['role'].queryset = company.company_roles.exclude(name='Owner')

    class Meta:
        model = CompanyClient
        fields = ('stakeholder_name', 'first_name', 'last_name', 'email', 'client_code', 'profile_pic', 'cell', 'address')


class ClientEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_pic'].widget = forms.FileInput()

    class Meta:
        model = CompanyClient
        fields = ('stakeholder_name', 'first_name', 'last_name', 'email', 'profile_pic', 'client_code',  'cell', 'address')


class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'file-widget.html'

    # def get_context(self, name, value, attrs):
    #     context = super().get_context(name, value, attrs)

        # print(name)
        # print(value)
        # print(attrs)
        # value.name = os.path.basename(value.name)
        # name = os.path.basename(name)
        # if value is not None:
            # print(context)
            # context['widget']['required'] = True
            # print(context['widget']['value'].url)
            # context['widget']['value'].name = os.path.basename(context['widget']['value'].name)
            # print(context['widget']['value'].url)
            # value.url = value.name
            # value.name = os.path.basename(value.name)
            # print(value.field)
            # print(value.url)
            # value.required = True
            # print(type(context['widget']['value'].name))
        # return context


class UserFileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget = CustomClearableFileInput()

    class Meta:
        model = UserFile
        fields = ('name', 'file')

class NewAnnouncementForm(forms.ModelForm):

    class Meta:
        model = Announcement
        fields = ('title', 'description')


UserFileFormSet = inlineformset_factory(User, UserFile, form=UserFileForm,
                                        extra=1, can_delete=True)


class CurrencyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ('currency_code',)
