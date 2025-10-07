import uuid
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone
from accounts.models import Department


class Contract(models.Model):
    TENDER = "tender"
    PRACTICE = "practice"
    DIRECT = "direct"
    PROTOCOL = "protocol"

    CONTRACT_TYPES = (
        (TENDER, "مناقصة"),
        (PRACTICE, "ممارسة"),
        (DIRECT, "أمر مباشر"),
        (PROTOCOL, "بروتوكول إسناد"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date_received = models.DateField(verbose_name="تاريخ ورود العقد")
    general_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الحصر العام")
    contract_number = models.CharField(max_length=50, verbose_name="رقم حصر العقود")
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPES, verbose_name="نوع العقد")
    content = models.TextField(verbose_name="مضمون العقد")
    progress = models.TextField(verbose_name="ما تم في العقد")
    archive_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الحفظ")
    end_date = models.DateField(blank=True, null=True, verbose_name="تاريخ الانتهاء")

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts",
        verbose_name="الإدارة",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_contracts",
        verbose_name="أُنشئ بواسطة",
    )

    file = models.FileField(upload_to="contracts/", blank=True, null=True, verbose_name="ملف العقد")

    class Meta:
        ordering = ["-date_received", "-id"]
        verbose_name = "عقد"
        verbose_name_plural = "العقود"

    def save(self, *args, **kwargs):
        # Default end_date to date_received + 2 years if not provided
        if not self.end_date and self.date_received:
            self.end_date = self.date_received + timedelta(days=365*2)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"عقد رقم {self.contract_number}"
