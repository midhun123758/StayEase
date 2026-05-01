from django.db import models
# Create your models here.
from App.models import User

class Hostel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hostels')
    name = models.CharField(max_length=255)
    address = models.TextField()
    location = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rooms_available = models.IntegerField(default=0)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return self.name
    
class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')                                                
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50)     
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)        
    room_members = models.ForeignKey(User,related_name='room_members',on_delete=models.CASCADE)
    def __str__(self):
        return f"Room {self.room_number} - {self.room_type}"        


class HostelImage(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="hostels/")

    def __str__(self):
        return f"Image of {self.hostel.name}"
    

class ChatRoom(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="chatrooms")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_rooms")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_rooms")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.username} - {self.hostel.name}"

class Hostler(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="hostlers"
    )

    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.CASCADE,
        related_name="hostlers"
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hostlers"
    )

    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)

    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name