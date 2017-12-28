from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class IsBusiness(permissions.BasePermission):
    def has_permission(self, request, view):

        if not hasattr(request.user.profile, 'profilebusiness'):
            raise PermissionDenied({"message": "You do not have business account"})
        else:
            return True
