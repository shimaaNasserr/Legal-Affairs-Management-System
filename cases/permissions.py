# permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class CasePermissions(BasePermission):
    """
    الصلاحيات:
    - GeneralManager و DepartmentManager (إدارة القضايا) لهم كل الصلاحيات
    - President: قراءة فقط
    - Lawyer (إدارة القضايا): يضيف ويعدل القضايا التي أنشأها
    - Secretary: يضيف ويعدل القضايا المتعلقة بالمحامي المخصص له
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # President and GeneralManager: full access
        if user.role_name in ["President", "GeneralManager"]:
            return True

        # GeneralManager: full access
        if user.role_name == "GeneralManager":
            return True

        # DepartmentManager: full access فقط لإدارة القضايا
        if user.role_name == "DepartmentManager":
            if hasattr(user, "department") and user.department and user.department.name == "إدارة القضايا":
                return True
            return False

        # Lawyer: read + create
        if user.role_name == "Lawyer" and hasattr(user, "department") and user.department and user.department.name == "إدارة القضايا":
            if request.method in SAFE_METHODS or request.method == "POST":
                return True
            # تعديل/حذف سيُتحكم فيه بالـ object-level
            return True

        # Secretary: read + create for cases related to their assigned lawyer
        if user.role_name == "Secretary" and hasattr(user, "assigned_lawyer"):
            if request.method in SAFE_METHODS or request.method == "POST":
                return True
            # تعديل/حذف سيُتحكم فيه بالـ object-level
            return True

        # أي دور آخر: لا صلاحية
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Read-only requests
        if request.method in SAFE_METHODS:
            if user.role_name in ["President", "GeneralManager"]:
                return True
            if user.role_name == "DepartmentManager" and hasattr(user, "department") and user.department and user.department.name == "إدارة القضايا":
                return True
            if user.role_name == "Lawyer" and obj.created_by == user:
                return True
            if user.role_name == "Secretary" and hasattr(user, "assigned_lawyer"):
                # Secretary can view cases created by their assigned lawyer
                return obj.created_by == user.assigned_lawyer
            return False

        # Write requests
        if user.role_name == "GeneralManager":
            return True
        if user.role_name == "DepartmentManager" and hasattr(user, "department") and user.department and user.department.name == "إدارة القضايا":
            return True
        if user.role_name == "Lawyer":
            return obj.created_by == user
        if user.role_name == "Secretary" and hasattr(user, "assigned_lawyer"):
            # Secretary can modify cases created by their assigned lawyer
            return obj.created_by == user.assigned_lawyer

        return False
