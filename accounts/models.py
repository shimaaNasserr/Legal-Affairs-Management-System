import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="اسم الدور"  # president, lawyer...
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="وصف الدور"   # "يملك جميع الصلاحيات" أو "يتابع التحقيقات"
    )

    class Meta:
        verbose_name = "دور"
        verbose_name_plural = "الأدوار"
        ordering = ["name"]
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True, verbose_name="اسم الإدارة")
    code = models.CharField(max_length=50, unique=True, verbose_name="كود الإدارة")

    class Meta:
        verbose_name = "إدارة"
        verbose_name_plural = "الإدارات"
        ordering = ["name"]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return self.name


#custom user model
class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")  
    username = models.CharField(max_length=150, verbose_name="اسم المستخدم") 
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="الدور"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="الإدارة"
    )
    #ده المحامي المسؤول اللي السكرتيره تابعه ليه
    assigned_lawyer = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="secretaries",
        verbose_name="المحامي المسؤول"
    )
    
    USERNAME_FIELD = "email" 
    REQUIRED_FIELDS = ["username"] 

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمين"

    @property
    def role_name(self):
        """إرجاع اسم الدور أو None إذا لم يكن هناك دور"""
        return self.role.name if self.role else None

    def __str__(self):
        return f"{self.username} - {self.role.name if self.role else 'بدون دور'}"
