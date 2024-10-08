from django.urls import path

from attendance.views import AttendanceView, punchIn, punchOut, AttendancePoilcyView, attendanceSearch, \
    AttendanceAdminView, employeeAttendanceSearch, deleteAttendancePolicy, editAttendancePolicyStatus, \
    editAttendancePolicy, attendancePolicies, ShiftView, deleteShift, edit_shift_form

urlpatterns = [
    path('attendance/', AttendanceView.as_view(), name='attendance'),
    path('attendanceAdmin/', AttendanceAdminView.as_view(), name='attendanceAdmin'),
    path('punchIn', punchIn, name='punchIn'),
    path('punchOut', punchOut, name='punchOut'),
    path('attendancePolicy/', AttendancePoilcyView.as_view(), name='attendancePolicy'),
    path('attendanceSearch', attendanceSearch, name='attendanceSearch'),
    path('employeeAttendanceSearch', employeeAttendanceSearch, name='employeeAttendanceSearch'),
    path('deleteAttendancePolicy/<int:pk>/', deleteAttendancePolicy, name='delete_attendance_policy'),
    path('editAttendancePolicyStatus/<int:pk>/<str:status>/', editAttendancePolicyStatus, name='edit_attendance_policy_status'),
    path('editAttendancePolicy/<int:pk>/', editAttendancePolicy, name='edit_attendance_policy'),
    path('attendancePolicies/', attendancePolicies, name='attendance_policies'),
    path('shift', ShiftView.as_view(), name='shift'),
    path('deleteShift/<int:pk>', deleteShift, name='delete_shift'),
    path('editShift/<int:pk>', edit_shift_form, name='edit_shift'),
    # path('editAttendancePunch/<int:pk>/', edit_attendacne_punch, name='edit_attendace_punch'),
    # path('attendance-requests/', attendance_request_admin_view, name='attendance_request_admin_view'),
]