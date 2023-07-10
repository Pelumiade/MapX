
from rest_framework.permissions import BasePermission

class IsSuperuserOrAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_superuser or request.user.is_admin)

class IsFieldOfficerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and not (request.user.is_superuser or request.user.is_admin) 
