# from django.db import models
# from App.models import User
# # Create your models here.
# class OwnerVerification(models.Model):

#     STATUS_CHOICES = (
#         ("PENDING", "Pending"),
#         ("APPROVED", "Approved"),
#         ("REJECTED", "Rejected"),
#     )

#     owner = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name="owner_verification"
#     )

#     aadhaar_front = models.URLField()
#     aadhaar_back = models.URLField()

#     selfie_image = models.URLField(
#         blank=True,
#         null=True
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default="PENDING"
#     )

#     rejection_reason = models.TextField(
#         blank=True,
#         null=True
#     )

#     verified_by = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="verified_owners"
#     )

#     verified_at = models.DateTimeField(
#         blank=True,
#         null=True
#     )

#     created_at = models.DateTimeField(
#         auto_now_add=True
#     )

#     updated_at = models.DateTimeField(
#         auto_now=True
#     )

#     def __str__(self):
#         return f"{self.owner.username} - {self.status}"