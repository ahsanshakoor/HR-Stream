import os

from django.db import models

# Create your models here.
from accounts.models import Company, User
from home.validator import MaxSizeValidator


def get_company_file_path(instance, filename):
    return 'company_{0}/{1}/{2}/{3}/{4}/{5}'.format(instance.company.id, 'files', 'file manager', instance.directory, instance.type, filename)


def get_company_bookmarks_path(instance, filename):
    return 'company_{0}/{1}/{2}'.format(instance.company.id,  'bookmarks', filename)


class Equipment(models.Model):

    Assigned = 'Assigned'
    Stocked = 'Stocked'
    Deployed = 'Deployed'
    Damaged = 'Damaged'
    Status = (
        (Assigned, 'Assigned'),
        (Damaged, 'Damaged'),
        (Deployed, 'Deployed'),
        (Stocked, 'Stocked')
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='equipments', null=True, blank=True)
    assign_to = models.ForeignKey(User, on_delete=models.PROTECT, related_name='equipment_assigned',
                                  null=True, blank=True)
    equipment_code = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=250, null=True, blank=True)
    model_number = models.CharField(max_length=50, null=True, blank=True)
    manufacturer = models.CharField(max_length=50, null=True, blank=True)
    purchase_date = models.DateField(blank=True, null=True)
    # purchase_from = models.CharField(max_length=50, null=True, blank=True)
    serial_number = models.PositiveIntegerField(null=True, blank=True)
    # warranty = models.PositiveIntegerField(null=True, blank=True)
    price = models.PositiveIntegerField(null=True, blank=True)
    # supplier = models.CharField(max_length=50, null=True, blank=True)
    # condition = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField( null=True, blank=True)
    status = models.CharField(max_length=10, verbose_name='Status Of Leave request', choices=Status, default=Stocked, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class DemoRequest(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    number = models.CharField(max_length=15, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


class Bookmark(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    link = models.CharField(max_length=1000, null=True, blank=True)
    icon = models.ImageField(upload_to=get_company_bookmarks_path, verbose_name='Icon', null=True, blank=True, validators=[MaxSizeValidator(5)])
    marked = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='bookmarks', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FileDirectoryType(models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='fileDirectoryType')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CompanyFile(models.Model):
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Uploaded By', related_name='userCompanyFiles', null=True, blank=True)
    shared_with = models.ManyToManyField(User, verbose_name='Shared With', related_name='userSharedFiles', blank=True)
    title = models.CharField(max_length=200, verbose_name='Title', null=True, blank=True)
    file = models.FileField(upload_to=get_company_file_path, verbose_name='File', validators=[MaxSizeValidator(5)], max_length=1000)
    type = models.CharField(max_length=200, verbose_name='File Type', null=True, blank=True)
    directory = models.ForeignKey(FileDirectoryType, on_delete=models.CASCADE, related_name='fileTypeCompanyFiles', verbose_name='File Directory', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='userFileCompany', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def filename(self):
        return os.path.basename(self.file.name)


