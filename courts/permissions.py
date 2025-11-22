from rest_framework.permissions import BasePermission


class CourtPermission(BasePermission):

    def has_permission(self, request, view):
        # Allow anyone authenticated to view
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        role_name = request.user.role_name
        
        if not role_name:
            return False

        # Full access for President & GeneralManager
        if role_name in ["President", "GeneralManager"]:
            return True

        # DepartmentManager can add/update courts for their own dept
        if role_name == "DepartmentManager":
            return True

        return False

    def has_object_permission(self, request, view, obj):
        role_name = request.user.role_name

        # Always allow viewing
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        if not role_name:
            return False

        # President & GeneralManager always allowed
        if role_name in ["President", "GeneralManager"]:
            return True

        # DepartmentManager only for their own courts
        if role_name == "DepartmentManager":
            return obj.department == request.user.department

        return False
