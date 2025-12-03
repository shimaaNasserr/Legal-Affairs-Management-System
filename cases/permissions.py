from rest_framework.permissions import BasePermission, SAFE_METHODS

class CasePermissions(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        # لازم يكون مسجل دخول
        if not user.is_authenticated:
            return False

        # أي حد داخل قسم القضايا يدخل على صفحة القضايا
        if hasattr(user, "department") and user.department and user.department.name == "إدارة القضايا":
            return True

        # رئيس الجامعة يشوف كل القضايا (قراءة فقط)
        if user.role_name == "President":
            if request.method in SAFE_METHODS:
                return True
            return False   # لا تعديل ولا إضافة

        # مدير إدارة القضايا يشوف ويعمل CRUD كامل
        if user.role_name == "GeneralManager":
            return True

        # المحامي: إضافة + قراءة + تعديل قضاياه فقط
        if user.role_name == "Lawyer":
            if request.method in SAFE_METHODS:
                return True
            if request.method == "POST":
                return True
            return True  # object-level permission هتتحكم بعدها

        # أي دور تاني → مالوش علاقة
        return False


    def has_object_permission(self, request, view, obj):
        user = request.user

        # Read-only requests allowed for President + Cases department
        if request.method in SAFE_METHODS:
            # رئيس الجامعة
            if user.role_name == "President":
                return True
            # قسم القضايا
            if hasattr(user, "department") and user.department and user.department.name == "إدارة القضايا":
                return True
            # المحامي يشوف قضاياه فقط
            if user.role_name == "Lawyer":
                return obj.created_by == user
            return False

        # WRITE permissions

        # مدير إدارة القضايا يقدر يعدّل أي قضية
        if (user.role_name == "GeneralManager" or
            (user.role_name == "DepartmentManager" and
            hasattr(user, "department") and
            user.department and
            user.department.name == "إدارة القضايا")):
            return True


        # المحامي يقدر يعدّل قضاياه فقط
        if user.role_name == "Lawyer":
            return obj.created_by == user

        # الباقي → مالوش أي صلاحية تعديل
        return False
