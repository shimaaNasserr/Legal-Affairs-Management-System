import uuid
from django.db import models
from accounts.models import Department


class Court(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="courts",
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class CourtDivision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name="divisions")
    name = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("court", "name")

    def __str__(self):
        return f"{self.court.name} - {self.name}"
