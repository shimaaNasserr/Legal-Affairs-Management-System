from rest_framework import permissions

class FatwaPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.role in ['President', 'GeneralManager']:
            return True
        if user.role == 'DepartmentManager':
            return request.method in permissions.SAFE_METHODS or request.method in ['POST', 'PUT', 'PATCH', 'DELETE']
        if user.role in ['Lawyer', 'Secretary']:
            return request.method in ['GET', 'POST']
        return False
