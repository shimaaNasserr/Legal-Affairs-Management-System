import uuid
import random
import string
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.apps import apps
from accounts.models import Department
from django.contrib.auth import get_user_model


User = get_user_model()


def allocate_general_number():
    """تخصيص رقم عام فريد للتحقيق"""
    now = timezone.now()
    year = now.year
    month = now.month
    random_part = ''.join(random.choices(string.digits, k=5))
    general_number = f"INV-{year}-{month:02d}-{random_part}"
    
    # التأكد من عدم تكرار الرقم
    Investigation = apps.get_model('investigations', 'Investigation')
    while Investigation.objects.filter(general_number=general_number).exists():
        random_part = ''.join(random.choices(string.digits, k=5))
        general_number = f"INV-{year}-{month:02d}-{random_part}"
    
    return general_number


class Investigation(models.Model):
    """نموذج التحقيقات"""
    
    INVESTIGATION_STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('under_investigation', 'قيد التحقيق'),
        ('completed', 'مكتمل'),
        ('closed', 'مغلق'),
        ('appealed', 'قيد الاستئناف'),
        ('referred_to_court', 'محال للقضاء'),
        ('settled', 'تم التسوية'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'عالية'),
        ('urgent', 'عاجلة'),
    ]
    
    CASE_TYPE_CHOICES = [
        ('against_university', 'ضد الجامعة'),
        ('by_university', 'مرفوعة من الجامعة'),
        ('internal_disciplinary', 'تأديبية داخلية'),
        ('academic_misconduct', 'مخالفة أكاديمية'),
        ('administrative', 'إدارية'),
    ]
    
    COMPLAINANT_TYPE_CHOICES = [
        ('student', 'طالب'),
        ('faculty_member', 'عضو هيئة تدريس'),
        ('employee', 'موظف'),
        ('external_party', 'طرف خارجي'),
        ('university', 'الجامعة'),
    ]
    
    # الحقول الأساسية
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    general_number = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name="الرقم العام"
    )
    
    # تفاصيل التحقيق
    title = models.CharField(max_length=200, verbose_name="عنوان التحقيق")
    description = models.TextField(verbose_name="وصف التحقيق")
    accused_names = models.TextField(
        verbose_name="أسماء المتهمين",
        help_text="يمكن إدخال أسماء متعددة مفصولة بفاصلة"
    )
    
    # التواريخ والحالة
    date_received = models.DateField(verbose_name="تاريخ الاستلام")
    date_started = models.DateField(null=True, blank=True, verbose_name="تاريخ بداية التحقيق")
    date_completed = models.DateField(null=True, blank=True, verbose_name="تاريخ انتهاء التحقيق")
    
    status = models.CharField(
        max_length=20,
        choices=INVESTIGATION_STATUS_CHOICES,
        default='pending',
        verbose_name="حالة التحقيق"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="الأولوية"
    )
    
    # حقول متخصصة للسياق الجامعي
    case_type = models.CharField(
        max_length=30,
        choices=CASE_TYPE_CHOICES,
        default='internal_disciplinary',
        verbose_name="نوع القضية"
    )
    
    complainant_type = models.CharField(
        max_length=20,
        choices=COMPLAINANT_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="نوع المشتكي"
    )
    
    complainant_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="اسم المشتكي"
    )
    
    complainant_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="رقم هوية/كود المشتكي"
    )
    
    faculty_college = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="الكلية المعنية"
    )
    
    # الملاحظات والنتائج
    notes = models.TextField(blank=True, default='', verbose_name="ملاحظات")
    findings = models.TextField(blank=True, default='', verbose_name="النتائج")
    recommendations = models.TextField(blank=True, default='', verbose_name="التوصيات")
    
    # الملف المرفق
    file = models.FileField(
        upload_to="investigations/",
        blank=True,
        null=True,
        verbose_name="الملف المرفق"
    )
    
    # الربط بالإدارة والمستخدمين
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='investigations',
        null=True,
        blank=True,
        verbose_name="الإدارة"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_investigations',
        null=True,
        blank=True,
        verbose_name="منشئ التحقيق"
    )
    
    assigned_investigators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_investigations',
        blank=True,
        verbose_name="المحققون المعينون"
    )
    
    # التواريخ التلقائية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        db_table = 'investigations'
        ordering = ['-created_at']
        verbose_name = "تحقيق"
        verbose_name_plural = "التحقيقات"
        indexes = [
            models.Index(fields=['general_number']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['date_received']),
            models.Index(fields=['department', 'status']),
        ]
    
    def __str__(self):
        return f"{self.general_number} - {self.title}"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        if self.date_received and self.date_received > timezone.now().date():
            raise ValidationError({
                'date_received': 'لا يمكن أن يكون تاريخ الاستلام في المستقبل'
            })
        
        if self.date_started and self.date_received and self.date_started < self.date_received:
            raise ValidationError({
                'date_started': 'لا يمكن أن يكون تاريخ بداية التحقيق قبل تاريخ الاستلام'
            })
        
        if self.date_completed and self.date_started and self.date_completed < self.date_started:
            raise ValidationError({
                'date_completed': 'لا يمكن أن يكون تاريخ انتهاء التحقيق قبل تاريخ البداية'
            })
    
    def save(self, *args, **kwargs):
        """حفظ النموذج مع تخصيص الرقم العام تلقائياً"""
        if not self.general_number:
            self.general_number = allocate_general_number()
        
        # تعيين إدارة افتراضية إذا لم تُحدد
        if not self.department_id:
            # يمكن تعديل هذا حسب منطق العمل
            default_dept = Department.objects.first()
            if default_dept:
                self.department = default_dept
        
        self.full_clean(exclude=['department'])
        super().save(*args, **kwargs)
    
    def get_accused_names_list(self):
        """إرجاع قائمة بأسماء المتهمين"""
        if self.accused_names:
            return [name.strip() for name in self.accused_names.split(',') if name.strip()]
        return []
    
    def set_accused_names_list(self, names_list):
        """تعيين أسماء المتهمين من قائمة"""
        if isinstance(names_list, list):
            self.accused_names = ', '.join(names_list)
        else:
            self.accused_names = str(names_list)


class Appeal(models.Model):
    """نموذج الاستئنافات المرتبطة بالتحقيقات"""
    
    APPEAL_STATUS_CHOICES = [
        ('submitted', 'مقدم'),
        ('under_review', 'قيد المراجعة'),
        ('accepted', 'مقبول'),
        ('rejected', 'مرفوض'),
        ('withdrawn', 'منسحب'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # ربط بالتحقيق
    investigation = models.ForeignKey(
        Investigation,
        on_delete=models.CASCADE,
        related_name='appeals',
        verbose_name="التحقيق"
    )
    
    complainant = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name="appeals",
        verbose_name="المشتكي",
        null=True,  # Add this temporarily
        blank=True  # Add this temporarily
    )
    
    # تفاصيل الاستئناف
    appeal_number = models.CharField(
        max_length=100, 
        unique=True, 
        blank=True,  # ADD THIS - allows empty for auto-generation
        verbose_name="رقم الاستئناف"
    )
    appellant_name = models.CharField(max_length=200, verbose_name="اسم المستأنف")
    appeal_reason = models.TextField(verbose_name="سبب الاستئناف")
    
    # التواريخ
    date_submitted = models.DateField(verbose_name="تاريخ تقديم الاستئناف")
    date_reviewed = models.DateField(null=True, blank=True, verbose_name="تاريخ المراجعة")
    
    # الحالة والنتيجة
    status = models.CharField(
        max_length=20,
        choices=APPEAL_STATUS_CHOICES,
        default='submitted',
        verbose_name="حالة الاستئناف"
    )
    
    decision = models.TextField(blank=True, default='', verbose_name="القرار")
    notes = models.TextField(blank=True, default='', verbose_name="ملاحظات")
    
    # الملف المرفق
    file = models.FileField(
        upload_to="appeals/",
        blank=True,
        null=True,
        verbose_name="ملف الاستئناف"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='appeals',
        verbose_name="الإدارة",
        null=True,  # مؤقتاً للترحيل
        blank=True  # مؤقتاً للترحيل
    )
    
    # المستخدم
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_appeals',
        verbose_name="منشئ الاستئناف"
    )
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_appeals',
        verbose_name="مراجع الاستئناف"
    )
    
    # التواريخ التلقائية
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        db_table = 'appeals'
        ordering = ['-created_at']
        verbose_name = "استئناف"
        verbose_name_plural = "الاستئنافات"
        indexes = [
            models.Index(fields=['appeal_number']),
            models.Index(fields=['status']),
            models.Index(fields=['date_submitted']),
            models.Index(fields=['investigation', 'status']),
        ]
    
    def __str__(self):
        return f"{self.appeal_number} - {self.appellant_name}"
    
    def clean(self):
        """التحقق من صحة البيانات"""
        # التحقق من التواريخ
        if self.date_submitted and self.date_submitted > timezone.now().date():
            raise ValidationError({
                'date_submitted': 'لا يمكن أن يكون تاريخ تقديم الاستئناف في المستقبل'
            })
        
        if self.date_reviewed and self.date_submitted and self.date_reviewed < self.date_submitted:
            raise ValidationError({
                'date_reviewed': 'لا يمكن أن يكون تاريخ المراجعة قبل تاريخ التقديم'
            })
        
        # التحقق من توافق الإدارة مع التحقيق
        if self.investigation and self.department and self.investigation.department != self.department:
            raise ValidationError({
                'department': 'يجب أن تكون الإدارة مطابقة لإدارة التحقيق'
            })
    
    def save(self, *args, **kwargs):
        """حفظ النموذج مع تخصيص الرقم تلقائياً"""
        # FIX: Use appeal_number instead of general_number
        if not self.appeal_number:
            self.appeal_number = self.allocate_appeal_number()
        
        # تعيين الإدارة من التحقيق إذا لم تُحدد
        if not self.department_id and self.investigation:
            self.department = self.investigation.department
        
        # تعيين المشتكي تلقائياً إذا لم يُحدد
        if not self.complainant_id and self.created_by:
            self.complainant = self.created_by
        
        super().save(*args, **kwargs)
    
    def allocate_appeal_number(self):
        """تخصيص رقم فريد للاستئناف"""
        now = timezone.now()
        year = now.year
        month = now.month
        random_part = ''.join(random.choices(string.digits, k=5))
        appeal_number = f"APL-{year}-{month:02d}-{random_part}"
        
        # استخدام self.__class__ بدلاً من Appeal مباشرة
        while self.__class__.objects.filter(appeal_number=appeal_number).exists():
            random_part = ''.join(random.choices(string.digits, k=5))
            appeal_number = f"APL-{year}-{month:02d}-{random_part}"
        
        return appeal_number
    
    def can_be_deleted(self):
        """التحقق من إمكانية حذف الاستئناف"""
        return self.investigation.status not in ['closed', 'completed']