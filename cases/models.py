import uuid
import random
import string
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.apps import apps
from accounts.models import Department

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_received = models.DateField()
    general_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    case_number = models.CharField(max_length=100)
    lawsuit_number = models.CharField(max_length=100)
    court = models.CharField(max_length=200)
    plaintiff = models.CharField(max_length=200)
    defendant = models.CharField(max_length=200)
    requests = models.TextField()
    hearing_dates = models.TextField(blank=True)
    notes = models.TextField(default='',blank=True)
    appeal_status = models.BooleanField(default=False)
    case_status = models.CharField(max_length=20, choices=CASE_STATUS_CHOICES, default='pending')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='cases', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_cases', null=True, blank=True)
    lawyers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='assigned_cases', blank=True)
    file = models.FileField(upload_to="cases/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
            self.department_id = 1
        self.full_clean(exclude=['department'])
        super().save(*args, **kwargs)

class LawyerSecretaryAccess(models.Model):
    lawyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lawyer_secretary_access", limit_choices_to={"role__name": "Lawyer"}, verbose_name="المحامي")
    secretary = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="secretary_lawyer_access", limit_choices_to={"role__name": "Secretary"}, verbose_name="السكرتيرة")

    class Meta:
        unique_together = ('lawyer', 'secretary')
        verbose_name = "صلاحية سكرتيرة لمحامي"
        verbose_name_plural = "صلاحيات السكرتيرات للمحامين"

    def __str__(self):
        return f"{self.secretary.username} يمكنها الوصول إلى {self.lawyer.username}"
