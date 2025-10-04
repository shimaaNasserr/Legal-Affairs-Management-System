from rest_framework import serializers
from .models import Fatwa

class FatwaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fatwa
        fields = '__all__'

    def validate(self, attrs):
        if not attrs.get('request_content'):
            raise serializers.ValidationError("request_content is required.")
        return attrs
