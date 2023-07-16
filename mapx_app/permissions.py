
from rest_framework.permissions import BasePermission

class IsSuperuserOrAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser or hasattr(request.user, 'admin'))

class IsFieldOfficerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'feo')
