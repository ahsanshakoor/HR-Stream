import django_filters

from task.models import Task
from accounts.models import User


class TaskFilter(django_filters.FilterSet):

    class Meta:
        model = Task
        fields = ('id', 'assign_to', 'title', 'status', 'priority', )

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filters['id'].label = ''
        self.filters['assign_to'].label = ''
        self.filters['title'].label = ''
        self.filters['status'].label = ''
        self.filters['priority'].label = ''
        self.filters['assign_to'].queryset = User.objects.filter(report_to=request.user.id)
        self.filters['id'].field.widget.attrs.update({'class': 'form-control', 'placeholder': "Search by ID", 'min': "0"})
        self.filters['assign_to'].field.widget.attrs.update({'class': 'form-control', 'placeholder': "Search by Assignee"})
        self.filters['title'].field.widget.attrs.update({'class': 'form-control', 'placeholder': "Search by Title"})
        self.filters['status'].field.widget.attrs.update( {'class': 'form-control', 'placeholder': "Search by Status"})
        self.filters['priority'].field.widget.attrs.update({'class': 'form-control', 'placeholder': " Search by Priority"})

    # @property
    # def qs(self):
    #     parent = super().qs
    #     user = getattr(self.request, 'user', None)
    #
    #     return parent.filter(assign_to=user.id)