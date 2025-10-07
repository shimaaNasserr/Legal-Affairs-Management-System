from rest_framework import permissions
from .models import LawyerSecretaryAccess

class CasePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role_name in ['President', 'GeneralManager']:
            return True
        if user.role_name == 'DepartmentManager':
            return obj.department == user.department
        if user.role_name == 'Lawyer':
            return obj.lawyers.filter(id=user.id).exists()
        if user.role_name == 'Secretary':
            allowed_lawyers = LawyerSecretaryAccess.objects.filter(secretary=user).values_list('lawyer_id', flat=True)
            return obj.lawyers.filter(id__in=allowed_lawyers).exists()
        return False
