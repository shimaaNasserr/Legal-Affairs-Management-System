import uuid
import random
import string
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.apps import apps

User = get_user_model()

def allocate_general_number():
    """تخصيص رقم عام فريد للفتوى"""
    now = timezone.now()
    year = now.year
    month = now.month
    random_part = ''.join(random.choices(string.digits, k=5))
    general_number = f"FTW-{year}-{month:02d}-{random_part}"
    
    # التأكد من عدم تكرار الرقم
    Fatwa = apps.get_model('fatwas', 'Fatwa')
    while Fatwa.objects.filter(general_number=general_number).exists():
        random_part = ''.join(random.choices(string.digits, k=5))
        general_number = f"FTW-{year}-{month:02d}-{random_part}"
    
    return general_number

class Fatwa(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    general_number = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="الرقم العام")
    department = models.ForeignKey('accounts.Department', on_delete=models.CASCADE, verbose_name="الإدارة")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="أنشئ بواسطة")
    request_content = models.TextField(verbose_name="محتوى الطلب")
    result = models.TextField(blank=True, null=True, verbose_name="النتيجة")
    file = models.FileField(upload_to='fatwas/', blank=True, null=True, verbose_name="الملف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "فتوى"
        verbose_name_plural = "الفتاوى"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['general_number']),
            models.Index(fields=['department']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.general_number:
            self.general_number = allocate_general_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"فتوى رقم {self.general_number}"
