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
