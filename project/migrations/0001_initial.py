# Generated by Django 3.0.2 on 2023-01-09 08:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import home.validator
import project.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_auto_20230109_0843'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Project')),
                ('code', models.CharField(max_length=100, verbose_name='Project Code')),
                ('description', models.TextField(verbose_name='Project Name')),
                ('start_date', models.DateField(verbose_name='Project Start Date')),
                ('end_date', models.DateField(verbose_name='Project End Date')),
                ('Project_status', models.CharField(blank=True, choices=[('start', 'Start'), ('finished', 'Finished'), ('in_progress', 'In Progress'), ('Pending', 'Pending')], default='Pending', max_length=25, null=True)),
                ('Project_state', models.BooleanField(default=False, verbose_name='Project State')),
                ('priority', models.CharField(blank=True, choices=[('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low')], default='High', max_length=25, null=True)),
                ('progress', models.CharField(blank=True, choices=[('0%', '0%'), ('10%', '10%'), ('20%', '20%'), ('30%', '30%'), ('40%', '40%'), ('50%', '50%'), ('60%', '60%'), ('70%', '70%'), ('80%', '80%'), ('90%', '90%'), ('100%', '100%')], default='0%', max_length=25, null=True)),
                ('rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Rate')),
                ('rate_type', models.CharField(blank=True, choices=[('Fixed', 'Fixed'), ('Hourly', 'Hourly')], default='Hourly', max_length=25, null=True)),
                ('estimated_time', models.PositiveIntegerField(blank=True, null=True, verbose_name='Estimated Time')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ManyToManyField(blank=True, related_name='project_clients', to='accounts.CompanyClient', verbose_name='Project Client')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='company_project', to='accounts.Company', verbose_name='Company')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_project', to=settings.AUTH_USER_MODEL, verbose_name='Project Created By')),
                ('lead_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_project_lead', to=settings.AUTH_USER_MODEL, verbose_name='Project Lead By')),
                ('team', models.ManyToManyField(related_name='user_project_team', to=settings.AUTH_USER_MODEL, verbose_name='Project Team')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(max_length=1000, upload_to=project.models.get_company_project_path, validators=[home.validator.MaxSizeValidator(5)], verbose_name='File')),
                ('type', models.CharField(blank=True, max_length=25, null=True, verbose_name='File Type')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='projectFileCompany', to='accounts.Company', verbose_name='Company')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_files', to='project.Project', verbose_name='Project Name')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_files', to=settings.AUTH_USER_MODEL, verbose_name='Uploaded By')),
            ],
        ),
    ]
