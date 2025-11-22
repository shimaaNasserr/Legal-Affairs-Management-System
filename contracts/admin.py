from django.contrib import admin
from .models import Contract

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = (
        "contract_number",
        "general_number",
        "contract_type",
        "date_received",
        "department",
        "created_by",
        "archive_date",
        "end_date",
    )
    list_filter = ("contract_type", "date_received", "archive_date", "department")
    search_fields = ("contract_number", "general_number", "content")
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('general_number', 'contract_number', 'contract_type', 'date_received')
        }),
        ('تفاصيل العقد', {
            'fields': ('content', 'progress', 'file')
        }),
        ('التواريخ', {
            'fields': ('archive_date', 'end_date')
        }),
        ('الربط', {
            'fields': ('department', 'created_by')
        }),
    )
    
    readonly_fields = ('created_by',)
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)