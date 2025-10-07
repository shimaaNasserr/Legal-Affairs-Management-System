from rest_framework import serializers
from django.utils import timezone
from .models import Contract

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/png",
    "image/jpeg",
}
MAX_FILE_SIZE_MB = 10


class ContractSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source="created_by.id")

    class Meta:
        model = Contract
        fields = [
            "id",
            "date_received",
            "general_number",
            "contract_number",
            "contract_type",
            "content",
            "progress",
            "archive_date",
            "end_date",
            "department",
            "created_by",
            "file",
        ]
        read_only_fields = ["created_by"]

    def validate_contract_type(self, value):
        valid_values = {c[0] for c in Contract.CONTRACT_TYPES}
        if value not in valid_values:
            raise serializers.ValidationError("نوع العقد غير صحيح.")
        return value

    def validate_file(self, value):
        if not value:
            return value
        content_type = getattr(value, "content_type", None)
        size = getattr(value, "size", 0)
        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError("صيغة الملف غير مدعومة. الصيغ المسموحة: PDF, DOC, DOCX, PNG, JPG.")
        if size and size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"حجم الملف يتجاوز {MAX_FILE_SIZE_MB} ميجابايت.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and not validated_data.get("created_by"):
            validated_data["created_by"] = request.user
            if request.user.department and not validated_data.get("department"):
                validated_data["department"] = request.user.department
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
