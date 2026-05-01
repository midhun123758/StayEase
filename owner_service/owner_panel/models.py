from django.db import models

# Create your models here.

from StayEase.Base_Panel.models import Hostel
class Hostel(models.Model):
   
    owner_user_id = models.IntegerField()
    name = models.CharField(max_length=255)
    address = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

    description = models.TextField(blank=True, null=True)

    rooms_available = models.IntegerField(default=0)
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (Owner ID: {self.owner_user_id})"