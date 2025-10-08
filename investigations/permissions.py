from rest_framework import permissions
from .models import Investigation


class InvestigationPermissions(permissions.BasePermission):
    """
    صلاحيات التحقيقات حسب الأدوار:
    - President/GeneralManager: صلاحيات كاملة
    - DepartmentManager: CRUD للتحقيقات التي تخص إدارته
    - Lawyer: عرض + إضافة (يمكن التعديل فقط من نفس الإدارة أو إذا معين له)
    - Secretary: عرض + إضافة للتحقيقات التي تخص المحامي المرتبط
    """
    
    def has_permission(self, request, view):
        """التحقق من الصلاحية العامة"""
        if not request.user.is_authenticated:
            return False
        
        # التأكد من وجود دور للمستخدم
        if not hasattr(request.user, 'role') or not request.user.role:
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """التحقق من الصلاحية على كائن محدد"""
        user = request.user
        
        # الحصول على اسم الدور
        role_name = user.role.name if user.role else None
        
        # President و GeneralManager: صلاحيات كاملة
        if role_name in ['President', 'GeneralManager']:
            return True
        
        # DepartmentManager: صلاحيات كاملة للتحقيقات في إدارته
        if role_name == 'DepartmentManager':
            return obj.department == user.department
        
        # Lawyer: يمكنه عرض وتعديل التحقيقات المعينة له أو من نفس الإدارة
        if role_name == 'Lawyer':
            # إذا كان معيناً كمحقق في هذا التحقيق
            if obj.assigned_investigators.filter(id=user.id).exists():
                return True
            
            # إذا كان من نفس الإدارة ولديه صلاحية
            if obj.department == user.department:
                # يمكنه العرض دائماً، والتعديل إذا كان منشئ التحقيق أو معيناً له
                if request.method in permissions.SAFE_METHODS:
                    return True
                return obj.created_by == user or obj.assigned_investigators.filter(id=user.id).exists()
            
            return False
        
        # Secretary: يمكنها عرض وإضافة التحقيقات المرتبطة بالمحامي المسؤول
        if role_name == 'Secretary':
            # التحقق من وجود محامي مسؤول
            if not user.assigned_lawyer:
                return False
            
            # يمكنها عرض التحقيقات المعينة للمحامي المسؤول
            if obj.assigned_investigators.filter(id=user.assigned_lawyer.id).exists():
                # العرض مسموح، التعديل محدود
                if request.method in permissions.SAFE_METHODS:
                    return True
                # يمكنها التعديل إذا كانت منشئة التحقيق
                return obj.created_by == user
            
            return False
        
        return False


class AppealPermissions(permissions.BasePermission):
    """صلاحيات الاستئنافات"""
    
    def has_permission(self, request, view):
        """التحقق من الصلاحية العامة"""
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'role') or not request.user.role:
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """التحقق من الصلاحية على كائن محدد"""
        user = request.user
        role_name = user.role.name if user.role else None
        
        # President و GeneralManager: صلاحيات كاملة
        if role_name in ['President', 'GeneralManager']:
            return True
        
        # DepartmentManager: صلاحيات للاستئنافات المرتبطة بتحقيقات إدارته
        if role_name == 'DepartmentManager':
            return obj.investigation.department == user.department
        
        # Lawyer: يمكنه التعامل مع الاستئنافات المرتبطة بتحقيقاته
        if role_name == 'Lawyer':
            investigation = obj.investigation
            # إذا كان معيناً كمحقق أو من نفس الإدارة
            if investigation.assigned_investigators.filter(id=user.id).exists():
                return True
            if investigation.department == user.department:
                return True
            return False
        
        # Secretary: يمكنها عرض الاستئنافات المرتبطة بالمحامي المسؤول
        if role_name == 'Secretary':
            if not user.assigned_lawyer:
                return False
            
            investigation = obj.investigation
            if investigation.assigned_investigators.filter(id=user.assigned_lawyer.id).exists():
                # العرض مسموح، التعديل محدود
                if request.method in permissions.SAFE_METHODS:
                    return True
                return obj.created_by == user
            
            return False
        
        return False


class InvestigationViewPermissions(permissions.BasePermission):
    """صلاحيات خاصة بعمليات العرض والإحصائيات"""
    
    def has_permission(self, request, view):
        """التحقق من الصلاحية للعمليات المختلفة"""
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'role') or not request.user.role:
            return False
        
        user = request.user
        role_name = user.role.name if user.role else None
        action = getattr(view, 'action', None)
        
        # الصلاحيات حسب العملية
        if action in ['list', 'retrieve', 'my_investigations', 'stats']:
            # جميع الأدوار يمكنها العرض والإحصائيات
            return role_name in ['President', 'GeneralManager', 'DepartmentManager', 'Lawyer', 'Secretary']
        
        elif action == 'create':
            # جميع الأدوار يمكنها الإضافة
            return role_name in ['President', 'GeneralManager', 'DepartmentManager', 'Lawyer', 'Secretary']
        
        elif action in ['update', 'partial_update']:
            # التحديث يحتاج صلاحيات خاصة (سيتم التحقق في has_object_permission)
            return role_name in ['President', 'GeneralManager', 'DepartmentManager', 'Lawyer', 'Secretary']
        
        elif action == 'destroy':
            # الحذف محدود للأدوار العليا فقط
            return role_name in ['President', 'GeneralManager']
        
        return True
