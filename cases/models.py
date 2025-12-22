import uuid
import random
import string
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from accounts.models import Department
from django.apps import apps
from courts.models import CourtDivision , Court


def allocate_general_number():
    now = timezone.now()
    year = now.year
    month = now.month
    random_part = ''.join(random.choices(string.digits, k=5))
    general_number = f"CASE-{year}-{month:02d}-{random_part}"

    Case = apps.get_model('cases', 'Case')
    while Case.objects.filter(general_number=general_number).exists():
        random_part = ''.join(random.choices(string.digits, k=5))
        general_number = f"CASE-{year}-{month:02d}-{random_part}"

    return general_number

class Case(models.Model):
    CASE_STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('under_study', 'قيد الدراسة'),
        ('in_court', 'قيد التقاضي'),
        ('closed', 'منتهية'),
        ('appealed', 'قيد الاستئناف'),
    ]

    OUTCOME_CHOICES = [
        ('for_university', 'لصالح الجامعة'),
        ('against_university', 'ضد الجامعة'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_received = models.DateField(verbose_name="تاريخ الاستلام")
    general_number = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="الرقم العام")
    case_number = models.CharField(max_length=100, verbose_name="رقم الحصر")
    lawsuit_number = models.CharField(max_length=100, verbose_name="رقم الدعوى")
    court = models.ForeignKey(Court, on_delete=models.PROTECT)
    division = models.ForeignKey(
        CourtDivision,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="cases"
    )
    plaintiff = models.CharField(max_length=200, verbose_name="اسم المدعي")
    defendant = models.CharField(max_length=200, verbose_name="اسم المدعى عليه")
    requests = models.TextField(verbose_name="الطلبات")
    
    hearing_dates = models.JSONField(default=list,  blank=True, verbose_name="تواريخ الجلسات")
    notes = models.TextField(default='', blank=True, verbose_name="ملاحظات")

    appeal_status = models.BooleanField(default=None, null=True, blank=True, verbose_name="حالة الاستئناف")
    case_status = models.CharField(max_length=20, choices=CASE_STATUS_CHOICES, default='pending', verbose_name="حالة القضية")
    
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='cases',
        null=True,
        blank=True,
        verbose_name="الإدارة"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_cases',
        null=True,
        blank=True,
        verbose_name="أنشئ بواسطة"
    )

    lawyers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_cases',
        blank=True,
        verbose_name="المحامون"
    )

    file = models.FileField(upload_to="cases/", blank=True, null=True, verbose_name="الملف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    ruling = models.CharField(max_length=20, choices=OUTCOME_CHOICES, blank=True, null=True, verbose_name="الحكم الصادر")
    saved_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الحفظ")

    class Meta:
        db_table = 'cases'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.case_number} - {self.plaintiff} vs {self.defendant}"

    def clean(self):
        if self.date_received and self.date_received > timezone.now().date():
            raise ValidationError({'date_received': 'لا يمكن أن يكون تاريخ الاستلام في المستقبل'})

    def save(self, *args, **kwargs):
        if not self.general_number:
            self.general_number = allocate_general_number()

        if not self.department_id:
            default_dept = Department.objects.first()
            if default_dept:
                self.department_id = default_dept.id

        self.full_clean(exclude=['department'])
        super().save(*args, **kwargs)
