from django.contrib import admin
from .models import Investigation, Appeal


@admin.register(Investigation)
class InvestigationAdmin(admin.ModelAdmin):
    """إدارة التحقيقات في لوحة الإدارة"""
    
    list_display = [
        'general_number', 'title', 'status', 'priority', 
        'department', 'created_by', 'date_received', 'created_at'
    ]
    
    list_filter = [
        'status', 'priority', 'department', 'date_received', 'created_at'
    ]
    
    search_fields = [
        'general_number', 'title', 'description', 'accused_names'
    ]
    
    readonly_fields = ['general_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('general_number', 'title', 'description', 'accused_names')
        }),
        ('التواريخ والحالة', {
            'fields': ('date_received', 'date_started', 'date_completed', 'status', 'priority')
        }),
        ('الملاحظات والنتائج', {
            'fields': ('notes', 'findings', 'recommendations'),
            'classes': ('collapse',)
        }),
        ('الملف والربط', {
            'fields': ('file', 'department', 'created_by', 'assigned_investigators')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['assigned_investigators']
    
    def get_queryset(self, request):
        """تخصيص QuerySet حسب صلاحيات المستخدم"""
        qs = super().get_queryset(request)
        
        # إذا كان المستخدم superuser، عرض جميع التحقيقات
        if request.user.is_superuser:
            return qs
        
        # إذا كان له دور، تطبيق الفلاتر حسب الدور
        role_name = request.user.role_name
        if role_name:
            if role_name in ['President', 'GeneralManager']:
                return qs
            elif role_name == 'DepartmentManager':
                return qs.filter(department=request.user.department)
            elif role_name == 'Lawyer':
                return qs.filter(assigned_investigators=request.user)
        
        return qs.none()


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    """إدارة الاستئنافات في لوحة الإدارة"""
    
    list_display = [
        'appeal_number', 'appellant_name', 'investigation', 
        'status', 'date_submitted', 'reviewed_by', 'created_at'
    ]
    
    list_filter = [
        'status', 'date_submitted', 'date_reviewed', 'created_at'
    ]
    
    search_fields = [
        'appeal_number', 'appellant_name', 'appeal_reason', 
        'investigation__title', 'investigation__general_number'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات الاستئناف', {
            'fields': ('investigation', 'appeal_number', 'appellant_name', 'appeal_reason')
        }),
        ('التواريخ والحالة', {
            'fields': ('date_submitted', 'date_reviewed', 'status')
        }),
        ('القرار والملاحظات', {
            'fields': ('decision', 'notes'),
            'classes': ('collapse',)
        }),
        ('الملف والمراجعة', {
            'fields': ('file', 'created_by', 'reviewed_by')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """تخصيص QuerySet حسب صلاحيات المستخدم"""
        qs = super().get_queryset(request)
        
        # إذا كان المستخدم superuser، عرض جميع الاستئنافات
        if request.user.is_superuser:
            return qs
        
        # إذا كان له دور، تطبيق الفلاتر حسب الدور
        role_name = request.user.role_name
        if role_name:
            if role_name in ['President', 'GeneralManager']:
                return qs
            elif role_name == 'DepartmentManager':
                return qs.filter(investigation__department=request.user.department)
            elif role_name == 'Lawyer':
                return qs.filter(investigation__assigned_investigators=request.user)
        
        return qs.none()
