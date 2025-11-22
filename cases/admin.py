from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Case


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = [
        'general_number', 
        'case_number', 
        'plaintiff', 
        'defendant', 
        'court', 
        'case_status',
        'department', 
        'created_by',
        'created_at',
    ]
    
    list_filter = [
        'case_status', 
        'appeal_status', 
        'department', 
        'created_at',
    ]
    
    search_fields = [
        'general_number', 
        'case_number', 
        'plaintiff', 
        'defendant',
        'court',
    ]
    
    filter_horizontal = ['lawyers']
    
    readonly_fields = [
        'general_number', 
        'created_by', 
        'created_at', 
        'updated_at',
    ]
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': (
                'general_number',
                'case_number', 
                'lawsuit_number',
                'date_received',
                'court'
            )
        }),
        ('أطراف القضية', {
            'fields': (
                'plaintiff',
                'defendant', 
                'requests'
            )
        }),
        ('التصنيف والمتابعة', {
            'fields': (
                'department',
                'case_status',
                'appeal_status',
                'lawyers'
            )
        }),
        ('تفاصيل إضافية', {
            'fields': (
                'hearing_dates',
                'notes',
                'file'
            ),
        }),
        ('معلومات النظام', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            ),
        }),
    )
    
    # إجراءات سريعة
    actions = ['mark_as_pending', 'mark_as_closed']
    
    ordering = ['-created_at']
    
    list_per_page = 25

    def mark_as_pending(self, request, queryset):
        """تعيين القضايا كقيد انتظار"""
        updated = queryset.update(case_status='pending')
        self.message_user(request, f'تم تعيين {updated} قضية كقيد انتظار')
    mark_as_pending.short_description = "تعيين كقيد انتظار"
    
    def mark_as_closed(self, request, queryset):
        """تعيين القضايا كمنتهية"""
        updated = queryset.update(case_status='closed')
        self.message_user(request, f'تم تعيين {updated} قضية كمنتهية')
    mark_as_closed.short_description = "تعيين كمنتهية"
    
    # حفظ المستخدم الحالي كمنشئ القضية
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # إذا كان إنشاء جديد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# تحسين عناوين الادمن - يجب أن تكون في ملف منفصل أو في urls.py
# سيتم نقلها إلى urls.py