from rest_framework.permissions import BasePermission

class IsPresident(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role_name = request.user.role_name
        # دعم كلا التنسيقين: "president" و "President"
        return role_name and role_name.lower() == "president"

class IsGeneralManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role_name = request.user.role_name
        # دعم كلا التنسيقين: "general_manager" و "GeneralManager"
        return role_name and (role_name.lower() == "general_manager" or role_name == "GeneralManager")

class IsDepartmentManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role_name = request.user.role_name
        # دعم كلا التنسيقين: "department_manager" و "DepartmentManager"
        return role_name and (role_name.lower() == "department_manager" or role_name == "DepartmentManager")

class IsLawyer(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role_name = request.user.role_name
        # دعم كلا التنسيقين: "lawyer" و "Lawyer"
        return role_name and role_name.lower() == "lawyer"

class IsSecretary(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        role_name = request.user.role_name
        # دعم كلا التنسيقين: "secretary" و "Secretary"
        return role_name and role_name.lower() == "secretary"
