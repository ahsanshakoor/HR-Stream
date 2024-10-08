# from django.contrib.auth.mixins import LoginRequiredMixin
from .decorators import require_user_access_rights
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .utils import user_has_access


class CompanyRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'company']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class PayrollsRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'payrolls']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class LeavePoliciesRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'leave_policies']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class AttendancePoliciesRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'attendance_policies']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class AdminDashboardRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'admin_dashboard']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class ProjectsRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'projects']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class PoliciesRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'policies']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class EquipmentRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'equipment']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class TimeLogRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'timelog']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class BookmarkRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'bookmark']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class FileManagerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'file_manager']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')


class PerformanceRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if user_has_access(request.user.id, ['owner', 'performance']):
            return super().dispatch(request, *args, **kwargs)
        else:
            return render(request, 'light/error-404.html')