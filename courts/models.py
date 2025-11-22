import uuid
from django.db import models
from accounts.models import Department


class Court(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name="اسم المحكمة")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="courts",
        null=True,
        blank=True,
        verbose_name="الإدارة"
    )

    class Meta:
        verbose_name = "محكمة"
        verbose_name_plural = "المحاكم"
        ordering = ["name"]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return self.name


class CourtDivision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name="divisions", verbose_name="المحكمة")
    name = models.CharField(max_length=255, verbose_name="اسم القسم")
    note = models.TextField(blank=True, null=True, verbose_name="ملاحظة")

    class Meta:
        unique_together = ("court", "name")
        verbose_name = "قسم محكمة"
        verbose_name_plural = "أقسام المحاكم"
        ordering = ["court", "name"]

    def __str__(self):
        return f"{self.court.name} - {self.name}"
