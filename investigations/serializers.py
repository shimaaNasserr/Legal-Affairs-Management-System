from rest_framework import serializers
from .models import Investigation, Appeal
from accounts.models import User
from django.utils import timezone


class InvestigationSerializer(serializers.ModelSerializer):
    """Serializer للتحقيقات مع دعم الملفات وأسماء المتهمين"""
    
    # حقول إضافية للعرض
    assigned_investigators_details = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    # تجاوز فحص الخيارات الافتراضي للسماح بإرسال التسميات العربية
    complainant_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    
    # حقل أسماء المتهمين كقائمة أو نص
    accused_names_list = serializers.SerializerMethodField()
    accused_names_input = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False,
        help_text="قائمة بأسماء المتهمين"
    )
    
    # إحصائيات الاستئنافات
    appeals_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Investigation
        fields = [
            'id', 'general_number', 'title', 'description', 'accused_names', 
            'accused_names_list', 'accused_names_input', 'date_received', 
            'date_started', 'date_completed', 'status', 'priority', 'case_type',
            'complainant_type', 'complainant_name', 'complainant_id', 'faculty_college',
            'notes', 'findings', 'recommendations', 'file', 'department', 'department_name',
            'created_by', 'created_by_name', 'assigned_investigators', 
            'assigned_investigators_details', 'appeals_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'general_number', 'created_at', 'updated_at']
    
    def validate_complainant_type(self, value):
        """Allow sending Arabic labels for complainant_type by mapping to keys."""
        if value in (None, ""):
            return None
        # Accept valid keys directly
        valid_keys = {k for k, _ in Investigation.COMPLAINANT_TYPE_CHOICES}
        if value in valid_keys:
            return value
        # Map Arabic labels to keys
        label_to_key = {label: key for key, label in Investigation.COMPLAINANT_TYPE_CHOICES}
        mapped = label_to_key.get(value)
        if mapped:
            return mapped
        raise serializers.ValidationError("قيمة غير صالحة لحقل نوع المشتكي")

    def get_assigned_investigators_details(self, obj):
        """إرجاع تفاصيل المحققين المعينين"""
        return [
            {
                'id': investigator.id,
                'username': investigator.username,
                'email': investigator.email,
                'role': investigator.role.name if investigator.role else None
            }
            for investigator in obj.assigned_investigators.all()
        ]
    
    def get_accused_names_list(self, obj):
        """إرجاع أسماء المتهمين كقائمة"""
        return obj.get_accused_names_list()
    
    def get_appeals_count(self, obj):
        """إرجاع عدد الاستئنافات المرتبطة"""
        return obj.appeals.count()
    
    def validate_date_received(self, value):
        """التحقق من صحة تاريخ الاستلام"""
        if value > timezone.now().date():
            raise serializers.ValidationError("لا يمكن أن يكون تاريخ الاستلام في المستقبل")
        return value
    
    def validate_date_started(self, value):
        """التحقق من صحة تاريخ بداية التحقيق"""
        if value and hasattr(self, 'initial_data'):
            date_received = self.initial_data.get('date_received')
            if date_received and value < timezone.datetime.strptime(date_received, '%Y-%m-%d').date():
                raise serializers.ValidationError("لا يمكن أن يكون تاريخ بداية التحقيق قبل تاريخ الاستلام")
        return value
    
    def validate_date_completed(self, value):
        """التحقق من صحة تاريخ انتهاء التحقيق"""
        if value and hasattr(self, 'initial_data'):
            date_started = self.initial_data.get('date_started')
            if date_started and value < timezone.datetime.strptime(date_started, '%Y-%m-%d').date():
                raise serializers.ValidationError("لا يمكن أن يكون تاريخ انتهاء التحقيق قبل تاريخ البداية")
        return value
    
    def validate_assigned_investigators(self, value):
        """التحقق من صحة المحققين المعينين"""
        for investigator in value:
            if not hasattr(investigator, 'role') or not investigator.role:
                raise serializers.ValidationError(f"المستخدم {investigator.username} ليس له دور محدد")
            # يمكن إضافة المزيد من التحقق حسب الحاجة
        return value
    
    def create(self, validated_data):
        """إنشاء تحقيق جديد"""
        # استخراج أسماء المتهمين إذا تم إرسالها كقائمة
        accused_names_input = validated_data.pop('accused_names_input', None)
        assigned_investigators_data = validated_data.pop('assigned_investigators', [])
        
        # إنشاء التحقيق
        investigation = Investigation.objects.create(**validated_data)
        
        # تعيين أسماء المتهمين
        if accused_names_input:
            investigation.set_accused_names_list(accused_names_input)
            investigation.save()
        
        # تعيين المحققين
        if assigned_investigators_data:
            investigation.assigned_investigators.set(assigned_investigators_data)
        
        return investigation
    
    def update(self, instance, validated_data):
        """تحديث التحقيق"""
        # استخراج أسماء المتهمين إذا تم إرسالها كقائمة
        accused_names_input = validated_data.pop('accused_names_input', None)
        assigned_investigators_data = validated_data.pop('assigned_investigators', None)
        
        # تحديث الحقول الأخرى
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # تحديث أسماء المتهمين
        if accused_names_input is not None:
            instance.set_accused_names_list(accused_names_input)
        
        instance.save()
        
        # تحديث المحققين المعينين
        if assigned_investigators_data is not None:
            instance.assigned_investigators.set(assigned_investigators_data)
        
        return instance


class AppealSerializer(serializers.ModelSerializer):
    """Serializer للاستئنافات"""
    
    # حقول إضافية للعرض
    investigation_title = serializers.CharField(source='investigation.title', read_only=True)
    investigation_general_number = serializers.CharField(source='investigation.general_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True)
    
    class Meta:
        model = Appeal
        fields = [
            'id', 'investigation', 'investigation_title', 'investigation_general_number',
            'appeal_number', 'appellant_name', 'appeal_reason', 'date_submitted',
            'date_reviewed', 'status', 'decision', 'notes', 'file',
            'created_by', 'created_by_name', 'reviewed_by', 'reviewed_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def validate_date_submitted(self, value):
        """التحقق من صحة تاريخ تقديم الاستئناف"""
        if value > timezone.now().date():
            raise serializers.ValidationError("لا يمكن أن يكون تاريخ تقديم الاستئناف في المستقبل")
        return value
    
    def validate_date_reviewed(self, value):
        """التحقق من صحة تاريخ مراجعة الاستئناف"""
        if value and hasattr(self, 'initial_data'):
            date_submitted = self.initial_data.get('date_submitted')
            if date_submitted and value < timezone.datetime.strptime(date_submitted, '%Y-%m-%d').date():
                raise serializers.ValidationError("لا يمكن أن يكون تاريخ المراجعة قبل تاريخ التقديم")
        return value
    
    def validate_appeal_number(self, value):
        """التحقق من عدم تكرار رقم الاستئناف"""
        if self.instance:
            # في حالة التحديث، استثناء الكائن الحالي من التحقق
            if Appeal.objects.filter(appeal_number=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("رقم الاستئناف موجود مسبقاً")
        else:
            # في حالة الإنشاء الجديد
            if Appeal.objects.filter(appeal_number=value).exists():
                raise serializers.ValidationError("رقم الاستئناف موجود مسبقاً")
        return value


class InvestigationStatsSerializer(serializers.Serializer):
    """Serializer لإحصائيات التحقيقات"""
    
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    under_investigation = serializers.IntegerField()
    completed = serializers.IntegerField()
    closed = serializers.IntegerField()
    appealed = serializers.IntegerField()
    
    # إحصائيات حسب الأولوية
    low_priority = serializers.IntegerField()
    medium_priority = serializers.IntegerField()
    high_priority = serializers.IntegerField()
    urgent_priority = serializers.IntegerField()
    
    # إحصائيات حسب الشهر الحالي
    this_month = serializers.IntegerField()
    last_month = serializers.IntegerField()


class InvestigationSummarySerializer(serializers.ModelSerializer):
    """Serializer مبسط للتحقيقات للعرض في القوائم"""
    
    department_name = serializers.CharField(source='department.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    appeals_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Investigation
        fields = [
            'id', 'general_number', 'title', 'status', 'priority', 'case_type',
            'complainant_type', 'complainant_name', 'faculty_college',
            'date_received', 'department_name', 'created_by_name',
            'appeals_count', 'created_at'
        ]
    
    def get_appeals_count(self, obj):
        return obj.appeals.count()
