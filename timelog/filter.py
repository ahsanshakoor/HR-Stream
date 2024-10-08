import django_filters

from accounts.models import User
from timelog.models import TimeLog


class TimeLogFilter(django_filters.FilterSet):

    class Meta:
        model = TimeLog
        fields = ('name', 'start_time', 'end_time')

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['name'].label = ''
        self.filters['start_time'].label = ''
        self.filters['end_time'].label = ''
        self.filters['name'].queryset = User.objects.filter(report_to=request.user.id)
        self.filters['name'].field.widget.attrs.update({'class': 'form-control', 'placeholder': "Search by Employees", })
        self.filters['start_time'].field.widget.attrs.update({'class': 'form-control', 'placeholder': "Search by Start Time"})
        self.filters['end_time'].field.widget.attrs.update({'class': 'form-control', 'placeholder': "Search by End Time"})


