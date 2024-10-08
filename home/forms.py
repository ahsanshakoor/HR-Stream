from django import forms
from django.forms import ClearableFileInput

from accounts.models import Company
from home.models import Equipment, Bookmark, CompanyFile, FileDirectoryType


class EquipmentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        company_name = kwargs.pop('company_name')
        super().__init__(*args, **kwargs)
        company = Company.objects.filter(name=company_name)
        company = company.first()
        self.fields['assign_to'].queryset = company.users.all()
        self.fields['equipment_code'].widget.attrs['readonly'] = True
        self.fields['purchase_date'].widget = forms.DateInput(attrs={'type': 'date'})

    class Meta:
        model = Equipment
        fields = ('name', 'model_number', 'manufacturer', 'purchase_date', 'serial_number', 'price',
                  'description', 'status', 'equipment_code', 'description', 'assign_to')


class EquipmentFormEdit(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['equipment_code'].widget.attrs['readonly'] = True
        self.fields['purchase_date'].widget = forms.DateInput(attrs={'type': 'date'})

    class Meta:
        model = Equipment
        fields = ('name', 'model_number', 'manufacturer', 'purchase_date', 'serial_number', 'price',
                  'description', 'status', 'equipment_code', 'description', 'assign_to')


class BookmarkForm(forms.ModelForm):

    class Meta:
        model = Bookmark
        fields = ('name', 'link', 'marked', 'icon')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CompanyFileForm(forms.ModelForm):

    max_upload_limit = 5 * 1024 * 1024

    class Meta:
        model = CompanyFile
        fields = ('title', 'file', 'directory')
        widgets = {
            'file': ClearableFileInput(attrs={'multiple': True}),
        }

    def __init__(self, *args, **kwargs):
        company_name = kwargs.pop('company_name')
        super().__init__(*args, **kwargs)
        company = Company.objects.filter(name=company_name)
        company = company.first()
        self.fields['directory'].queryset = FileDirectoryType.objects.filter(company=company)


class FileDirectoryTypeForm(forms.ModelForm):
    class Meta:
        model = FileDirectoryType
        fields = ('name',)