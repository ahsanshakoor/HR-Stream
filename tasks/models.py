import os

from django.db import models
from accounts.models import User, Company
from project.models import Project
from home.validator import MaxSizeValidator


def get_company_task_path(instance, filename):
    return 'company_{0}/{1}/{2}/{3}/{4}'.format(instance.company.id, 'files',  'task', instance.type, filename)


def get_company_card_files_path(instance, filename):
    return 'company_{0}/{1}/{2}/{3}'.format(instance.company.id, 'cards', 'files', filename)


class Task(models.Model):
    START = 'start'
    FINISHED = 'finished'
    IN_PROGRESS = 'in_progress'
    PENDING = 'pending'
    ON_HOLD = 'on hold'
    UNDER_REVIEW = 'under review'
    STATUS = (
        # (START, 'Start'),
        (FINISHED, 'Finished'),
        (IN_PROGRESS, 'In Progress'),
        (PENDING, 'Pending'),
        (ON_HOLD, 'On Hold'),
        (UNDER_REVIEW, 'Under Review'),
    )
    High = 'High'
    Medium = 'Medium'
    Low = 'Low'
    PRIORITY = (
        (High, 'High'),
        (Medium, 'Medium'),
        (Low, 'Low'),
    )
    ZERO = '0'
    TEN = '10'
    TWENTY = '20'
    THIRTY = '30'
    FOURTY = '40'
    FIFTY = '50'
    SIXTY = '60'
    SEVENTY = '70'
    EIGHTY = '80'
    NINTY = '90'
    HUNDRED = '100'
    PROGRESS = (
        (ZERO, '0'),
        (TEN, '10'),
        (TWENTY, '20'),
        (THIRTY, '30'),
        (FOURTY, '40'),
        (FIFTY, '50'),
        (SIXTY, '60'),
        (SEVENTY, '70'),
        (EIGHTY, '80'),
        (NINTY, '90'),
        (HUNDRED, '100'),
    )
    name = models.CharField(max_length=125, verbose_name='Task Title')
    description = models.TextField(verbose_name='Task Description', null=True, blank=True)
    priority = models.CharField(max_length=25, choices=PRIORITY, default=Medium, verbose_name='Task Priority')
    due_date = models.DateField(verbose_name='Due Date', null=True)
    status = models.CharField(max_length=25, choices=STATUS, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='Project Name', related_name='task_project')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='taskCompany')
    assign_to = models.ManyToManyField(User, verbose_name='Employee', related_name='task_assignee')
    follower = models.ManyToManyField(User, verbose_name='Follower', related_name='task_follower')
    progress = models.CharField(max_length=25, choices=PROGRESS, default=ZERO, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Task Created By', related_name='task_creator', null=True)

    def __str__(self):
        return str(self.name)


class TaskFiles(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name='Task', related_name='task_files')
    file = models.FileField(upload_to=get_company_task_path, verbose_name='File', validators=[MaxSizeValidator(5)], max_length=1000)
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Uploaded By', related_name='user_task_files')
    type = models.CharField(max_length=8, verbose_name='File Type')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='taskFileCompany')

    def __str__(self):
        return str(self.task)

    def filename(self):
        return os.path.basename(self.file.name)


class Board(models.Model):
    name = models.CharField(max_length=100, verbose_name='Board Title')
    color = models.CharField(max_length=10, verbose_name='Board Title')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_board', verbose_name='Project Name')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='boardCompany')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)


class Card(models.Model):
    class Meta:
        ordering = ('-updated_at',)

    FINISHED = 'finished'
    IN_PROGRESS = 'in_progress'
    PENDING = 'pending'
    ON_HOLD = 'on_hold'
    UNDER_REVIEW = 'under_review'
    STATUS = (
        (FINISHED, 'Finished'),
        (IN_PROGRESS, 'In Progress'),
        (PENDING, 'Pending'),
        (ON_HOLD, 'On Hold'),
        (UNDER_REVIEW, 'Under Review'),
    )
    High = 'High'
    Medium = 'Medium'
    Low = 'Low'
    PRIORITY = (
        (High, 'High'),
        (Medium, 'Medium'),
        (Low, 'Low'),
    )
    ZERO = '0'
    TEN = '10'
    TWENTY = '20'
    THIRTY = '30'
    FOURTY = '40'
    FIFTY = '50'
    SIXTY = '60'
    SEVENTY = '70'
    EIGHTY = '80'
    NINTY = '90'
    HUNDRED = '100'
    PROGRESS = (
        (ZERO, '0'),
        (TEN, '10'),
        (TWENTY, '20'),
        (THIRTY, '30'),
        (FOURTY, '40'),
        (FIFTY, '50'),
        (SIXTY, '60'),
        (SEVENTY, '70'),
        (EIGHTY, '80'),
        (NINTY, '90'),
        (HUNDRED, '100'),
    )
    name = models.CharField(max_length=125, verbose_name='Card Title')
    description = models.TextField(verbose_name='Card Description', null=True, blank=True)
    priority = models.CharField(max_length=25, choices=PRIORITY, default=Medium, verbose_name='Card Priority')
    due_date = models.DateTimeField(verbose_name='Due Date', null=True)
    status = models.CharField(max_length=25, choices=STATUS, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='board_cards', verbose_name='Board Name')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Company', related_name='cardCompany')
    assign_to = models.ManyToManyField(User, verbose_name='Employee', related_name='card_assignee')
    follower = models.ManyToManyField(User, verbose_name='Follower', related_name='card_follower')
    progress = models.CharField(max_length=25, choices=PROGRESS, default=ZERO, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Card Created By',
                                   related_name='card_creator', null=True)
    archived = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class CardFile(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='CardFiles')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='cardfiles')
    # name = models.CharField(max_length=350)
    file = models.FileField(upload_to=get_company_card_files_path, max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.filename()

    def delete(self, using=None, keep_parents=False):
        self.file.delete()
        super().delete(using, keep_parents)

    def save(self, *args, **kwargs):
        try:
            # is the object in the database yet?
            obj = CardFile.objects.get(id=self.id)
        except CardFile.DoesNotExist:
            # object is not in db, nothing to worry about
            return super().save(*args, **kwargs)
            # is the save due to an update of the actual image file?
        if obj.file and self.file and obj.file != self.file:
            # delete the old image file from the storage in favor of the new file
            obj.file.delete()
        return super().save(*args, **kwargs)

    def filename(self):
        return os.path.basename(self.file.name)