#encoding=utf8

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


def group_required(group, login_url=None, raise_exception=False, redirect_url="/error"):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if neccesary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_group(user):
        # First check if the user has the permission (even anon users)
        if user.groups.filter(name=group):
            return True
        # In case the 403 handler should be called raise the exception
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_group, redirect_url)
