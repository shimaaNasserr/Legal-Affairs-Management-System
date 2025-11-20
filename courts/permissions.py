from rest_framework.permissions import BasePermission


class CourtPermission(BasePermission):

    def has_permission(self, request, view):
        # Allow anyone authenticated to view
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        role = request.user.role

        # Full access for President & GeneralManager
        if role in ["President", "GeneralManager"]:
            return True

        # DepartmentManager can add/update courts for their own dept
        if role == "DepartmentManager":
            return True

        return False

    def has_object_permission(self, request, view, obj):
        role = request.user.role

        # Always allow viewing
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # President & GeneralManager always allowed
        if role in ["President", "GeneralManager"]:
            return True

        # DepartmentManager only for their own courts
        if role == "DepartmentManager":
            return obj.department == request.user.department

        return False
