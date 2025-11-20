from rest_framework import serializers
from .models import Fatwa

class FatwaSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)
    class Meta:
        model = Fatwa
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('request_content'):
            raise serializers.ValidationError("request_content is required.")
        return attrs
