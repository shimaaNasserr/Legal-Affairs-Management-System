from django.conf import settings
from django.db import models, transaction

# simple global sequence model (if you already have one, use that)
class GlobalSequence(models.Model):
    name = models.CharField(max_length=100, unique=True)
    next_number = models.BigIntegerField(default=1)

    @classmethod
    def next_for(cls, name):
        with transaction.atomic():
            obj, _ = cls.objects.select_for_update().get_or_create(name=name)
            val = obj.next_number
            obj.next_number += 1
            obj.save(update_fields=["next_number"])
        return val

# class Appeal(models.Model):
#     # assumed fields — adjust/extend as necessary
#     general_number = models.BigIntegerField(unique=True, null=True, blank=True)
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     # relationships (assume Investigation, Department exist)
#     investigation = models.ForeignKey(
#         "investigations.Investigation",
#         on_delete=models.CASCADE,
#         related_name="appeals"
#     )
#     department = models.ForeignKey(
#         "departments.Department",
#         on_delete=models.PROTECT,
#         related_name="appeals"
#     )

#     complainant = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.PROTECT,
#         related_name="filed_appeals"
#     )

#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="created_appeals"
#     )

#     class Meta:
#         ordering = ["-created_at"]

#     def save(self, *args, **kwargs):
#         # ensure general_number is set from global sequence if not provided
#         if not self.general_number:
#             self.general_number = GlobalSequence.next_for("appeal_general_number")
#         super().save(*args, **kwargs)

#     def can_be_deleted(self) -> bool:
#         """
#         Prevent deletion if linked investigation is closed.
#         Adjust logic if your Investigation model stores state differently.
#         """
#         inv = self.investigation
#         status = getattr(inv, "status", None)
#         if status and str(status).lower() == "closed":
#             return False
#         return True
