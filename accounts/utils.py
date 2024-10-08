from django.shortcuts import _get_queryset
from django.utils import timezone

from accounts.exceptions.custom import ObjectNotFound
from hashlib import sha1
from accounts.models import User, Role


def is_user_owner(user_id):
    user = User.objects.filter(id=user_id).prefetch_related('role').first()
    for role in user.role.all():
        if role.name == 'Owner':
            return True
    return False


def user_has_access(user_id, require_permissions_list):
    user = User.objects.filter(id=user_id).prefetch_related('role')
    roles_ids = user.first().role.values_list('pk', flat=True)
    qs_permissions = Role.objects.filter(id__in=roles_ids).prefetch_related('role_permissions')
    permissions_list = [list(p.role_permissions.values_list('name_value', flat=True)) for p in qs_permissions]
    for require_permission in require_permissions_list:
        for permission_set in permissions_list:
            if require_permission in permission_set:
                return True
    return False


def get_company_object_from_user(user_id):
    user = get_object_or_404_template_default(User.objects.select_related('company'), id=user_id)
    return user.company


def get_object_or_404_template(klass, template, *args, **kwargs):
    # replacement for django.shortcuts.get_object_or_404()
    # allows a template to be supplied instead of a 404

    """
    Uses get() to return an object, or raises a Http404 exception if the object
    does not exist.
    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.
    Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
    object is found.
    """

    queryset = _get_queryset(klass)

    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        raise ObjectNotFound(template)


def get_object_or_404_template_default(klass, *args, **kwargs):
    return get_object_or_404_template(klass, 'light/error-404.html', *args, **kwargs)


def get_sha1_filename(filename=''):
    encoding = 'utf-8'
    now = timezone.now().strptime('%Y-%m-%d_%H:%M:%S')
    print(now)
    filename = now + '_' + filename
    return sha1(filename.encode(encoding)).hexdigest()
