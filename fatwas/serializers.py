from rest_framework import serializers
from .models import Fatwa

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
}
MAX_FILE_SIZE_MB = 10

class FatwaSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    class Meta:
        model = Fatwa
        fields = '__all__'

    def validate(self, attrs):
        # Require request_content only on create, or when explicitly provided in update
        if self.instance is None:
            if not attrs.get('request_content'):
                raise serializers.ValidationError("request_content is required.")
        else:
            # On update, if request_content is provided, ensure it's not empty
            if 'request_content' in attrs and not attrs.get('request_content'):
                raise serializers.ValidationError("request_content cannot be empty.")
        return attrs

    def validate_file(self, value):
        if not value:
            return value
        content_type = getattr(value, "content_type", None)
        size = getattr(value, "size", 0)
        if content_type and content_type not in ALLOWED_CONTENT_TYPES:
            raise serializers.ValidationError("صيغة الملف غير مدعومة. الصيغة المسموحة: PDF.")
        if size and size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"حجم الملف يتجاوز {MAX_FILE_SIZE_MB} ميجابايت.")
        return value
