from django.urls import path

from project.views import ProjectView, ProjectsView, get_project_edit_form, update_project_priority, \
    update_project_state, delete_project, delete_project_list, project_search, delete_file, assign_member, assign_lead, \
    update_project_progress

urlpatterns = [
    path('project/<int:pk>/', ProjectView.as_view(), name='project'),
    path('projects/', ProjectsView.as_view(), name='projects'),
    path('projects/<str:list>/', ProjectsView.as_view(), name='project_list'),
    path('project/<int:pk>/delete/', delete_project, name='delete_project'),
    path('project/<int:pk>/<str:type>/edit/', get_project_edit_form, name='project_edit'),
    path('project/<int:pk>/<str:priority>/<str:type>/', update_project_priority, name='edit_project_priority'),
    path('projectProgress/<int:pk>/<str:progress>/', update_project_progress, name='edit_project_progress'),
    path('project/<int:pk>/<str:state>/edit/', update_project_state, name='edit_project_state'),
    path('project/<int:pk>/delete/', delete_project, name='delete_project'),
    path('projectList/<int:pk>/delete/', delete_project_list, name='delete_project_list'),
    path('project/<int:pk>/delete/project/file/', delete_file, name='delete_file'),
    path('project/<str:type>/', project_search, name='project_search'),
    path('project/', project_search, name='project_search'),
    path('assignMember/<int:project>/<int:user>', assign_member, name='assign_member'),
    path('assignLead/<int:project>/<int:user>', assign_lead, name='assign_lead'),
]