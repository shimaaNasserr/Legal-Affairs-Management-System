from rest_framework import serializers
from .models import Fatwa

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/png",
    "image/jpeg",
}
MAX_FILE_SIZE_MB = 10

class FatwaSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    class Meta:
        model = Fatwa
        fields = '__all__'
        extra_kwargs = {
            "request_content": {
                "required": True,
                "allow_blank": False,
                "min_length": 5,
                "error_messages": {
                    "required": "محتوى الطلب مطلوب.",
                    "blank": "محتوى الطلب لا يمكن أن يكون فارغًا.",
                    "min_length": "محتوى الطلب يجب ألا يقل عن 5 أحرف.",
                },
            },
        }

    def validate(self, attrs):
        content = attrs.get('request_content')
        if isinstance(content, str) and not content.strip():
            raise serializers.ValidationError({"request_content": "محتوى الطلب لا يمكن أن يكون فارغًا."})
        return attrs

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
        if request and request.user:
            validated_data.setdefault("created_by", request.user)
            if request.user.department:
                validated_data.setdefault("department", request.user.department)
        return super().create(validated_data)
