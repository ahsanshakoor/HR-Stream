from django.forms import models
from django import forms
from todo.models import Todo


class addTodoForm(models.ModelForm):

    class Meta:
        model = Todo
        fields = ('title',)
        widgets = {
            'title': forms.Textarea(attrs={'placeholder': 'Add Goal Here', 'box-sizing': 'border-box;', 'resize': 'none;'}),
        }

