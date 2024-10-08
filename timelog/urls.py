
from django.urls import path

from timelog.views import TimeLogView, reject, approve, timelogDetails, singleTimeLog, DeleteTimeLog, get_task, \
    get_time_log_calender, update_time_log, manual_time_log, edit_timeLog_table, TimeLogAdmin, timelog_status, \
    delete_time_log_table, approve_time_log, company_manual_task_name, delete_manual_task_name, \
    create_n_edit_manual_task_name

urlpatterns = [
    path('time_log/', TimeLogView.as_view(), name='time_log'),
    path('time_log/<str:table>/', TimeLogView.as_view(), name='time_log'),
    path('time_log_manual/', manual_time_log, name='time_log_manual'),
    path('time_log_manual/<str:table>/', manual_time_log, name='time_log_manual'),
    path('update_time_log/', update_time_log, name='update_time_log'),
    path('time_log/<str:table>/', TimeLogView.as_view(), name='time_log_table'),
    path('time_log/update/', update_time_log, name='time_log_update'),
    path('time_log/<int:pk>/<int:log>/', TimeLogView.as_view(), name='time_log'),
    path('time_log/<int:log>/', TimeLogView.as_view(), name='time_log'),
    path('Approve_time_log/<int:pk>/', approve, name='approve'),
    path('Reject_time_log/<int:pk>/', reject, name='reject'),
    path('timelogDetails/', timelogDetails, name='timelogDetails'),
    path('time_log_details/', TimeLogAdmin.as_view(), name='time_log_details'),
    path('time_log_details_approve/', approve_time_log, name='time_log_approve'),
    path('singleTimelog/<int:pk>/', singleTimeLog, name='singleTimeLog'),
    path('delete_time_log/<int:pk>/', DeleteTimeLog.as_view(), name='delete_time_log'),
    path('delete_time_log/<int:pk>/<str:table>', delete_time_log_table, name='deleteTimelogTable'),
    path('task/<int:pro_id>/get/', get_task, name='getTask'),
    path('task_event/', get_time_log_calender, name='getTimeLogCalender'),
    path('edit_timelog_table/<int:time_id>', edit_timeLog_table, name='editTimelogTable'),
    path('timelog_status/<int:timelog_id>/<str:name>', timelog_status, name='timelog_status_update'),
    path('manual_task_name/new/', create_n_edit_manual_task_name, name='createManualTaskName'),
    path('manual_task_name/<int:manual_task_name_id>/edit/', create_n_edit_manual_task_name, name='editManualTaskName'),
    path('manual_task_name/<int:manual_task_name_id>/delete/', delete_manual_task_name, name='deleteManualTaskName'),
    path('manual_task_name/', company_manual_task_name, name='showManualTaskName'),

]