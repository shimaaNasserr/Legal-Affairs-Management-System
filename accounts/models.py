import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta

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


# -------- UserManager مع دعم create_superuser --------
class UserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def get_deactivated_users(self):
        return super().get_queryset().filter(
            is_active=False, 
            deleted_at__isnull=True,
            deactivated_at__isnull=False
        )

    def get_users_for_deletion(self):
        fifteen_days_ago = timezone.now() - timedelta(days=15)
        return super().get_queryset().filter(
            is_active=False,
            deactivated_at__lte=fifteen_days_ago,
            deleted_at__isnull=True
        )
        
    def get_by_natural_key(self, username):
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username})

    # إضافة create_user
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # إضافة create_superuser
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# -------- User Model --------
class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")  
    username = models.CharField(max_length=150, verbose_name="اسم المستخدم")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    deactivated_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ التعطيل")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الحذف النهائي")
    deactivated_until = models.DateTimeField(null=True, blank=True)
    objects = UserManager()
    all_objects = models.Manager()  # To access all users including deactivated ones
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
    # ده المحامي المسؤول اللي السكرتيره تابعه ليه
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
        return self.role.name if self.role else None

    def soft_delete(self):
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save(update_fields=['is_active', 'deactivated_at'])
    
    def reactivate(self):
        if not self.is_active and self.deactivated_at:
            self.is_active = True
            self.deactivated_at = None
            self.save(update_fields=['is_active', 'deactivated_at'])
    
    def delete(self, *args, **kwargs):
        self.soft_delete()
    
    def hard_delete(self):
        super().delete()
    
    def __str__(self):
        status = 'معطل' if not self.is_active else 'نشط'
        return f"{self.username} - {self.role.name if self.role else 'بدون دور'} ({status})"


# -------- Password Reset Token --------
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.token}"
