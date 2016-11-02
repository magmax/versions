from rest_framework import permissions
from django.conf import settings

class IsRegistered(permissions.BasePermission):
    def _is_valid_email(self, request):
        if request.user.is_anonymous:
            return False
        if '@' not in request.user.email:
            return False
        name, domain = request.user.email.split('@')
        return domain == settings.COMPANY_DOMAIN

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS and self._is_valid_email(request):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in permissions.SAFE_METHODS and self._is_valid_email(request):
            return True
        return False
