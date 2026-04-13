from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def save(self, *args, **kwargs):
        if self.role != 'hostler':
            self.owner = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username