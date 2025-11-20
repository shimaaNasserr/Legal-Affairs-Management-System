from rest_framework import serializers
from .models import Court, CourtDivision


class CourtDivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourtDivision
        fields = ["id", "name", "note"]


class CourtSerializer(serializers.ModelSerializer):
    divisions = CourtDivisionSerializer(many=True, read_only=True)

    class Meta:
        model = Court
        fields = ["id", "name", "description", "department", "divisions"]
