from rest_framework.permissions import BasePermission

class CourtPermission(BasePermission):
    def has_permission(self, request, view):
        # أي مستخدم مسجل الدخول مسموح له يشوف قائمة المحاكم
        if request.method in ["GET", "HEAD", "OPTIONS", "POST"]:
            return request.user.is_authenticated

        # PUT/PATCH/DELETE حسب الدور
        role_name = request.user.role_name
        if role_name in ["President", "GeneralManager"]:
            return True
        if role_name == "DepartmentManager":
            return True  # على المحاكم التابعة لقسمه
        return False

    def has_object_permission(self, request, view, obj):
        # عرض المحاكم لأي مستخدم مسموح
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        role_name = request.user.role_name
        if role_name in ["President", "GeneralManager"]:
            return True
        if role_name == "DepartmentManager":
            return obj.department == request.user.department
        return False
