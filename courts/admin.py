from django.contrib import admin
from .models import Court, CourtDivision


class CourtDivisionInline(admin.TabularInline):
    model = CourtDivision
    extra = 1
    verbose_name = "قسم المحكمة"
    verbose_name_plural = "أقسام المحكمة"


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "description")
    search_fields = ("name", "description")
    list_filter = ("department",)
    inlines = [CourtDivisionInline]
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('name', 'description', 'department')
        }),
    )


@admin.register(CourtDivision)
class CourtDivisionAdmin(admin.ModelAdmin):
    list_display = ("name", "court", "note")
    search_fields = ("name", "court__name", "note")
    list_filter = ("court",)
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('court', 'name', 'note')
        }),
    )
