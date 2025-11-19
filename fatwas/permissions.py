from rest_framework import permissions

class FatwaPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        role_name = None
        try:
            role_name = (user.role.name if hasattr(user, "role") and user.role else None) or None
        except Exception:
            role_name = None

        # Normalize
        role_name = (role_name or "").lower()

        if role_name in ["president", "general_manager"]:
            return True

        if role_name == "department_manager":
            # Allow read and write within department-level workflows
            return request.method in permissions.SAFE_METHODS or request.method in ["POST", "PUT", "PATCH", "DELETE"]

        if role_name in ["lawyer", "secretary"]:
            # Read and create only
            return request.method in ["GET", "POST"]

        return False
