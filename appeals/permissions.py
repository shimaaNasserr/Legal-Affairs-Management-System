from rest_framework import permissions
from investigations.models import Investigation

class IsAppealAllowed(permissions.BasePermission):
    """
    الصلاحيات المخصصة للاستئنافات بناءً على الأدوار
    """
    
    def get_user_role(self, user):
        """الحصول على دور المستخدم كسلسلة نصية"""
        if not hasattr(user, 'role') or not user.role:
            return None
        
        # إذا كان role كائن، احصل على اسمه، وإلا حوله إلى سلسلة
        if hasattr(user.role, 'name'):
            return user.role.name
        else:
            return str(user.role)
    
    def has_permission(self, request, view):
        user = request.user
        
        # تحقق إذا كان المستخدم مصادق عليه
        if not user.is_authenticated:
            return False
        
        user_role = self.get_user_role(user)
        print(f"PERMISSION DEBUG: User {user.username} with role {user_role}")
        print(f"PERMISSION DEBUG: Request method {request.method}")
        
        if user_role in ['president', 'general_manager']:
            print("PERMISSION: President/GeneralManager - All access granted")
            return True
        
        if user_role == 'department_manager':
            print("PERMISSION: DepartmentManager - Checking permissions")
            if request.method in permissions.SAFE_METHODS:
                return True
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                return True
            return True
        
        if user_role == 'lawyer':
            print("PERMISSION: Lawyer - Read and Create access")
            return request.method in ['GET', 'POST', 'HEAD', 'OPTIONS']
        
        if user_role == 'secretary':
            print("PERMISSION: Secretary - Read and Create access")
            return request.method in ['GET', 'POST', 'HEAD', 'OPTIONS']
        
        print(f"PERMISSION: No matching role found for {user_role}")
        return False
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        user_role = self.get_user_role(user)
        
        print(f"OBJECT PERMISSION DEBUG: User {user.username} with role {user_role}")
        print(f"OBJECT PERMISSION DEBUG: Object department {obj.department}, User department {getattr(user, 'department', 'No department')}")
        
        if user_role in ['president', 'general_manager']:
            print("OBJECT PERMISSION: President/GeneralManager - Full access")
            return True
        
        if user_role == 'department_manager':
            has_access = obj.department == user.department
            print(f"OBJECT PERMISSION: DepartmentManager - Access {'granted' if has_access else 'denied'}")
            return has_access
        
        if user_role == 'lawyer':
            if request.method in permissions.SAFE_METHODS:
                has_access = obj.investigation in user.assigned_investigations.all()
                print(f"OBJECT PERMISSION: Lawyer read - Access {'granted' if has_access else 'denied'}")
                return has_access
            elif request.method == 'POST':
                investigation_id = request.data.get('investigation')
                if investigation_id:
                    try:
                        investigation = Investigation.objects.get(id=investigation_id)
                        has_access = investigation in user.assigned_investigations.all()
                        print(f"OBJECT PERMISSION: Lawyer create - Access {'granted' if has_access else 'denied'}")
                        return has_access
                    except Investigation.DoesNotExist:
                        return False
                return False
        
        if user_role == 'secretary':
            if hasattr(user, 'supervising_lawyer') and user.supervising_lawyer:
                lawyer = user.supervising_lawyer
                if request.method in permissions.SAFE_METHODS:
                    has_access = obj.investigation in lawyer.assigned_investigations.all()
                    print(f"OBJECT PERMISSION: Secretary read - Access {'granted' if has_access else 'denied'}")
                    return has_access
                elif request.method == 'POST':
                    investigation_id = request.data.get('investigation')
                    if investigation_id:
                        try:
                            investigation = Investigation.objects.get(id=investigation_id)
                            has_access = investigation in lawyer.assigned_investigations.all()
                            print(f"OBJECT PERMISSION: Secretary create - Access {'granted' if has_access else 'denied'}")
                            return has_access
                        except Investigation.DoesNotExist:
                            return False
            return False
        
        print("OBJECT PERMISSION: No permission granted")
        return False