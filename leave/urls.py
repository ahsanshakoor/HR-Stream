from django.urls import path

from leave.views import LeavePolicyView, LeavePoliciesView, LeaveView, \
    EmployeeLeave, AdminLeave, leaveRequestSearch, leaveStatus, editLeaveRequest, deleteLeaveRequest, \
    leave_policy_status, editLeavePolicy, delete_leave_policy, get_leave_type, edit_leave_type, delete_leave_type, \
    leave_type_status, getRemainingDays

urlpatterns = [
    path('leavePolicy/', LeavePolicyView.as_view(), name='leavepolicy'),
    path('leavePolicies/', LeavePoliciesView.as_view(), name='leavepolicies'),
    path('editLeavePolicy/<int:pk>/', editLeavePolicy, name='edit_leave_policy'),
    path('editLeaveType/<int:leave>/', edit_leave_type, name='edit_leave_type'),
    path('leavePolicyType/<int:pk>/', get_leave_type, name='get_leave_type'),
    path('deleteLeavePolicy/<int:pk>/', delete_leave_policy, name='delete_leave_policy'),
    path('deleteLeavePolicyType/<int:pk>/', delete_leave_type, name='delete_leave_type'),
    # path('holiday/<int:pk>', holiday, name='holiday'),
    # path('holiday/new', addHolidays, name='new_holiday'),
    path('leaveType/', LeaveView.as_view(), name='leave_type'),
    path('leaveType/<int:pk>/', LeaveView.as_view(), name='leave_type'),
    path('leave/', EmployeeLeave.as_view(), name='leave'),
    path('leaveAdmin/', AdminLeave.as_view(), name='leave_admin'),
    path('leaveSearch/', leaveRequestSearch, name='search_leave'),
    path('edirLeavePolicyStatus/<int:pk>/<str:status>', leave_policy_status, name='edit_leave_policy_status'),
    path('edirLeaveTypeStatus/<int:pk>/<str:status>', leave_type_status, name='edit_leave_type_status'),
    path('approveLeaveRequest/<int:request_id>/<str:name>', leaveStatus, name='status_update'),
    path('editLeaveRequest/<int:pk>/<str:user>', editLeaveRequest, name='edit_leave_request'),
    path('deleteLeaveRequest/<int:pk>/<str:user>', deleteLeaveRequest, name='delete_leave_request'),
    path('getRemainingDays/<int:pk>/<int:user>/', getRemainingDays, name='get_remaining_days'),

]