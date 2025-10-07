from rest_framework import serializers
from .models import Case, LawyerSecretaryAccess
from accounts.models import User
from django.utils import timezone

class CaseSerializer(serializers.ModelSerializer):
    lawyers_details = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Case
        fields = [
            'id', 'date_received', 'general_number', 'case_number', 'lawsuit_number',
            'court', 'plaintiff', 'defendant', 'requests', 'hearing_dates', 'notes',
            'appeal_status', 'case_status', 'department', 'department_name', 'created_by',
            'created_by_name', 'lawyers', 'lawyers_details', 'file', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'general_number', 'created_at', 'updated_at']

    def get_lawyers_details(self, obj):
        return [{'id': lawyer.id, 'username': lawyer.username, 'email': lawyer.email} for lawyer in obj.lawyers.all()]

    def validate_date_received(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("لا يمكن أن يكون تاريخ الاستلام في المستقبل")
        return value

    def validate_lawyers(self, value):
        for lawyer in value:
            if not hasattr(lawyer, 'role') or not lawyer.role or lawyer.role.name.lower() != 'lawyer':
                raise serializers.ValidationError(f"المستخدم {lawyer.username} ليس محامياً")
        return value

    def create(self, validated_data):
        lawyers_data = validated_data.pop('lawyers', [])
        case = Case.objects.create(**validated_data)
        if lawyers_data:
            case.lawyers.set(lawyers_data)
        return case

    def update(self, instance, validated_data):
        lawyers_data = validated_data.pop('lawyers', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if lawyers_data is not None:
            instance.lawyers.set(lawyers_data)
        return instance

class LawyerSecretaryAccessSerializer(serializers.ModelSerializer):
    lawyer_name = serializers.CharField(source='lawyer.username', read_only=True)
    secretary_name = serializers.CharField(source='secretary.username', read_only=True)
    lawyer_email = serializers.CharField(source='lawyer.email', read_only=True)
    secretary_email = serializers.CharField(source='secretary.email', read_only=True)

    class Meta:
        model = LawyerSecretaryAccess
        fields = ['id', 'lawyer', 'lawyer_name', 'lawyer_email', 'secretary', 'secretary_name', 'secretary_email']

    def validate(self, data):
        if data['lawyer'].role_name != 'Lawyer':
            raise serializers.ValidationError({"lawyer": "المستخدم المحدد ليس محامياً"})
        if data['secretary'].role_name != 'Secretary':
            raise serializers.ValidationError({"secretary": "المستخدم المحدد ليس سكرتيرة"})
        return data
