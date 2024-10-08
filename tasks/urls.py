from django.urls import path
from tasks.views import TaskView, update_task_status, delete_task, assign_task_modal, assign_task, open_chat, \
    TaskBoardView, add_task_to_board, edit_task_form, delete_task_from_board, assign_lead, assign_member, add_board, \
    edit_task_board_form, delete_board, add_card, edit_card_form, delete_card, add_task_form, \
    update_task_status_on_board_change, update_card_on_board_change, update_card_status, get_card, expand_tasks_list, \
    ArchivedTaskBoardView, toggle_archive_tasks

urlpatterns = [
    path('tasks/', TaskView.as_view(), name='tasks'),
    path('taskBoard/<int:pk>/', TaskBoardView.as_view(), name='task_board'),
    path('ataskBoard/<int:pk>/', ArchivedTaskBoardView.as_view(), name='atask_board'),
    path('tasks/<int:pk>/', TaskView.as_view(), name='tasks_project'),
    path('tasks/<int:pk>/<str:status>/', TaskView.as_view(), name='tasks_with_status'),
    path('taskUpdate/<int:pk>/', update_task_status, name='update_task_status'),
    path('taskDelete/<int:pk>/', delete_task, name='delete_task'),
    path('boardDelete/<int:pk>/', delete_board, name='delete_board'),
    path('taskDeleteFromBoard/<int:pk>/', delete_task_from_board, name='delete_task_from_board'),
    path('assignTaskModal/<int:project_id>/<int:task_id>/', assign_task_modal, name='assign_task_modal'),
    path('assignTask/<int:assignee>/<int:task>/', assign_task, name='assign_task'),
    path('openChat/<int:pk>', open_chat, name='open_chat'),
    # path('addTaskToBoard/<str:type>/', add_task_to_board, name='add_task_to_board'),
    path('addTaskToBoard/<int:pk>/<str:status>/', add_task_form, name='add_task_to_form'),
    path('editTaskOnBoard/<int:pk>/', edit_task_form, name='edit_task_on_board'),
    path('editTaskBoard/<int:pk>/', edit_task_board_form, name='edit_task_board'),
    path('assignMemberOnBoard/<int:project>/<int:user>', assign_member, name='assign_member_on_board'),
    path('assignLeadOnBoard/<int:project>/<int:user>', assign_lead, name='assign_lead_on_board'),
    path('addBoard/', add_board, name='add_board'),
    path('addCard/<int:pk>', add_card, name='add_card'),
    path('CardDelete/<int:pk>/', delete_card, name='delete_card'),
    path('EditCard/<int:pk>', edit_card_form, name='edit_card'),
    path('GetCard/<int:pk>/', get_card, name='get_card'),
    path('cardUpdate/<int:pk>/', update_card_status, name='update_card_status'),
    path('taskBoard/<int:project_id>/update_task_status/', update_task_status_on_board_change, name='update_task_status_on_board_change'),
    path('taskBoard/<int:project_id>/update_card/', update_card_on_board_change, name='update_card_on_board_change'),
    path('expanded_tasks_list/<int:project_id>/<int:board_id>/', expand_tasks_list, name='expand_tasks_list'),
    path('updateArchiveTasks/<str:status>/<int:card_id>/', toggle_archive_tasks, name='toggle_archive_tasks'),
]