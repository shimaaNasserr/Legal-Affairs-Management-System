from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_general_number():
    last = Fatwa.objects.all().order_by('-id').first()
    if not last:
        return 1
    return last.general_number + 1

class Fatwa(models.Model):
    general_number = models.PositiveIntegerField(unique=True, blank=True, null=True)
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    request_content = models.TextField()
    result = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='fatwas/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.general_number:
            self.general_number = generate_general_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Fatwa #{self.general_number}"
