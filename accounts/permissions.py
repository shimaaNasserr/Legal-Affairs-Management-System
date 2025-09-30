from rest_framework.permissions import BasePermission

class IsPresident(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == "president"

class IsGeneralManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == "general_manager"

class IsDepartmentManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == "department_manager"

class IsLawyer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == "lawyer"

class IsSecretary(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == "secretary"
