from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="الاسم")

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"
        ordering = ["name"]

    def __str__(self):
        return self.name
