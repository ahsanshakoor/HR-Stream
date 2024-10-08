from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from functools import wraps
# from accounts.models import User, Role
from accounts.utils import user_has_access


def require_user_access_rights(require_access_rights_list):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if user_has_access(request.user.id, require_access_rights_list):
                return func(request, *args, **kwargs)
            else:
                return render(request, 'light/error-404.html')  #PermissionDenied('You are not allowed to visit this page')
            # user = User.objects.filter(id=request.user.id).prefetch_related('role')
            # roles_ids = user.first().role.values_list('pk', flat=True)
            # qs_permissions = Role.objects.filter(id__in=roles_ids).prefetch_related('role_permissions')
            # permissions_list = [list(p.role_permissions.values_list('name_value', flat=True)) for p in qs_permissions]
            # for require_permission in require_permissions_list:
            #     for permission_set in permissions_list:
            #         if require_permission in permission_set:
            #             return func(request, *args, **kwargs)
            # raise PermissionDenied
        # inner.__name__ = func.__name__
        # inner.__doc__ = func.__doc__
        # inner.__dict__ = func.__dict__

        return inner
    return decorator
