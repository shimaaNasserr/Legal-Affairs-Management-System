from django.contrib import admin
from .models import Court, CourtDivision


class CourtDivisionInline(admin.TabularInline):
    model = CourtDivision
    extra = 1


@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ("name", "department")
    search_fields = ("name",)
    list_filter = ("department",)
    inlines = [CourtDivisionInline]


@admin.register(CourtDivision)
class CourtDivisionAdmin(admin.ModelAdmin):
    list_display = ("name", "court")
    search_fields = ("name", "court__name")
