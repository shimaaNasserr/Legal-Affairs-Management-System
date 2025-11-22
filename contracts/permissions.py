from rest_framework.permissions import BasePermission, SAFE_METHODS


class ContractPermissions(BasePermission):
    """
    - president, general_manager: full access
    - department_manager: CRUD, but restricted to their department
    - lawyer, secretary: read-only EXCEPT they may PATCH only the 'file' field on items in their department
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role_name = user.role_name
        if request.method in SAFE_METHODS:
            return True
        # write operations
        if not role_name:
            return False
        # توحيد الأسماء - استخدام Capitalized
        role_name_normalized = role_name if role_name[0].isupper() else role_name.replace('_', '').title()
        if role_name_normalized in {"President", "GeneralManager"}:
            return True
        if role_name_normalized == "DepartmentManager":
            return True
        if role_name_normalized in {"Lawyer", "Secretary"}:
            # Will be enforced in has_object_permission to only allow PATCH with 'file'
            return request.method == "PATCH"
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        role_name = user.role_name
        if not role_name:
            return False
            
        # توحيد الأسماء
        role_name_normalized = role_name if role_name[0].isupper() else role_name.replace('_', '').title()
        
        if request.method in SAFE_METHODS:
            # Visibility: restrict to department for non-admin roles
            if role_name_normalized in {"President", "GeneralManager"}:
                return True
            return obj.department_id == getattr(getattr(user, "department", None), "id", None)
        # Writes
        if role_name_normalized in {"President", "GeneralManager"}:
            return True
        if role_name_normalized == "DepartmentManager":
            # Can manage only within their department
            return obj.department_id == getattr(getattr(user, "department", None), "id", None)
        if role_name_normalized in {"Lawyer", "Secretary"} and request.method == "PATCH":
            # Only allow updating 'file' within department
            if obj.department_id != getattr(getattr(user, "department", None), "id", None):
                return False
            # If serializer present, ensure only 'file' is being updated
            if hasattr(view, "request") and hasattr(view.request, "data"):
                allowed_keys = {"file"}
                incoming_keys = set(view.request.data.keys())
                # Allow partial update that only includes 'file'
                return incoming_keys.issubset(allowed_keys)
            return False
        return False
