from rest_framework import permissions

class FatwaPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # استخدام role_name property
        role_name = user.role_name
        
        # Normalize
        role_name = (role_name or "").lower()

        if role_name in ["president", "general_manager"]:
            return True

        if role_name == "department_manager":
            # Allow read and write within department-level workflows
            return request.method in permissions.SAFE_METHODS or request.method in ["POST", "PUT", "PATCH", "DELETE"]

        if role_name in ["lawyer", "secretary"]:
            # Read-only
            return request.method in permissions.SAFE_METHODS

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        role_name = (getattr(user, "role_name", None) or "").lower()

        if request.method in permissions.SAFE_METHODS:
            # Admins see all, others only their department
            if role_name in ["president", "general_manager"]:
                return True
            return obj.department_id == getattr(getattr(user, "department", None), "id", None)

        # Write operations
        if role_name in ["president", "general_manager"]:
            return True
        if role_name == "department_manager":
            return obj.department_id == getattr(getattr(user, "department", None), "id", None)
        # Lawyers/secretaries cannot modify/delete
        return False
