from django.urls import path
from django.views.generic import TemplateView
from task.views import TaskView, DeleteTask, UpdateTask, SingleTask, SingleTaskUpdate, start_task

urlpatterns = [
    path('task/', TaskView.as_view(), name='task'),
    path('delete_task/<str:pk>/', DeleteTask.as_view(), name='delete_task'),
    path('update_task/<int:pk>/', UpdateTask.as_view(), name='update_task'),
    path('singleTask/<str:pk>/', SingleTask.as_view(), name='singleTask'),
    path('singleTaskUpdate/<str:pk>/', SingleTaskUpdate.as_view(), name='singleTaskUpdate'),
    path('singleTaskStart/<str:pk>/', start_task, name='singleTaskStart'),

]