from rest_framework import serializers
from investigations.models import Appeal
from investigations.models import Investigation

class AppealSerializer(serializers.ModelSerializer):
    investigation_title = serializers.CharField(source='investigation.title', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    complainant_name = serializers.CharField(source='complainant.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Appeal
        fields = '__all__'  # Use this to include all fields
        read_only_fields = ['appeal_number', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        print("=== DEBUG: Serializer create method ===")
        print(f"Validated data: {validated_data}")
        return super().create(validated_data)