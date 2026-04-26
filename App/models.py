from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):

    ROLE_CHOICES = (
        ('user', 'User'),
        ('hostler', 'Hostler'),
        ('owner', 'Owner'),
        ('admin', 'Admin'),
    )
    email = models.EmailField(unique=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    owner = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clients'
    )

    is_google_user = models.BooleanField(default=False)
    kyc_completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.role != 'hostler':
            self.owner = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)  # ✅ ADD THIS
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)
    
class KycDocument(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    id_proof = models.FileField(upload_to='kyc/id_proofs/')
    address = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    status = models.CharField(max_length=10, default='pending')



