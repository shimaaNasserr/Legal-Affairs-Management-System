from rest_framework import serializers
from .models import Case, LawyerSecretaryAccess
from accounts.models import User
from django.utils import timezone

class CaseSerializer(serializers.ModelSerializer):
    # ======= SerializerMethodFields =======
    court_name = serializers.SerializerMethodField()
    division_name = serializers.SerializerMethodField()
    court_full_name = serializers.SerializerMethodField()
    lawyers_details = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    date_received = serializers.DateField(allow_null=True, required=False)
    saved_date = serializers.DateField(allow_null=True, required=False)

    class Meta:
        model = Case
        fields = [
            'id',
            'court',
            'court_name',
            'division_name',
            'court_full_name',
            'case_number',
            'general_number',  
            'lawsuit_number',
            'plaintiff',
            'defendant',
            'requests',
            'hearing_dates',
            'notes',
            'appeal_status',
            'case_status',
            'ruling',
            'saved_date',
            'date_received',
            'file',
            'department',
            'department_name',
            'created_by',
            'created_by_name',
            'lawyers',
            'lawyers_details',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    # ======= Court & Division =======
    def get_court_name(self, obj):
        return obj.court.name if obj.court else "-"

    def get_division_name(self, obj):
        try:
            return obj.court.division.name if obj.court and obj.court.division else "-"
        except AttributeError:
            return "-"

    def get_court_full_name(self, obj):
        court = self.get_court_name(obj)
        division = self.get_division_name(obj)
        return f"{court} - {division}" if division != "-" else court

    # ======= Lawyers details =======
    def get_lawyers_details(self, obj):
        return [
            {'id': l.id, 'username': l.username, 'email': l.email}
            for l in obj.lawyers.all()
        ]

    # ======= Validations =======
    def validate_date_received(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("لا يمكن أن يكون تاريخ الاستلام في المستقبل")
        return value
    
    def validate(self, attrs):
        if attrs.get("date_received") == "":
            attrs["date_received"] = None
        if attrs.get("saved_date") == "":
            attrs["saved_date"] = None
        return attrs

    def validate_lawyers(self, value):
        for lawyer in value:
            role_name = getattr(lawyer, 'role_name', None)
            if not role_name or role_name.lower() != 'lawyer':
                raise serializers.ValidationError(f"المستخدم {lawyer.username} ليس محامياً")
        return value

    # ======= Create & Update =======
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

# ======= Serializer for Lawyer-Secretary Access =======
class LawyerSecretaryAccessSerializer(serializers.ModelSerializer):
    lawyer_name = serializers.CharField(source='lawyer.username', read_only=True)
    secretary_name = serializers.CharField(source='secretary.username', read_only=True)
    lawyer_email = serializers.CharField(source='lawyer.email', read_only=True)
    secretary_email = serializers.CharField(source='secretary.email', read_only=True)

    class Meta:
        model = LawyerSecretaryAccess
        fields = [
            'id',
            'lawyer',
            'lawyer_name',
            'lawyer_email',
            'secretary',
            'secretary_name',
            'secretary_email'
        ]

    def validate(self, data):
        if getattr(data['lawyer'], 'role_name', '').lower() != 'lawyer':
            raise serializers.ValidationError({"lawyer": "المستخدم المحدد ليس محامياً"})
        if getattr(data['secretary'], 'role_name', '').lower() != 'secretary':
            raise serializers.ValidationError({"secretary": "المستخدم المحدد ليس سكرتيرة"})
        return data
