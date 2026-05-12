
from django.utils import timezone
from datetime import timedelta
from django.db import models
# Create your models here.
from App.models import User
from django.conf import settings
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
    mess_service =models.BooleanField(default=False)  # True if sent by messaging service, False if sent by user
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    image1=models.ImageField(upload_to="hostels/", blank=True, null=True)
    image2=models.ImageField(upload_to="hostels/", blank=True, null=True)
    image3=models.ImageField(upload_to="hostels/", blank=True, null=True)
    image4=models.ImageField(upload_to="hostels/", blank=True, null=True)
    def __str__(self):
        return self.name
    

class HostelDocument(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    file_url = models.URLField()   # S3 link
    document_type = models.CharField(max_length=50)

    uploaded_at = models.DateTimeField(auto_now_add=True)


class Room(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')                                                
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50)     
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)        
    bed_space =models.IntegerField(default=1)  # Number of bed spaces in the room

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type}"        

class Room_image(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="Rooms/")
    def __str__(self):
        return f"Image of {self.room.room_number}"
    

class ChatRoom(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="chatrooms")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_rooms")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner_rooms")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.username} - {self.hostel.name}"

class Hostler(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="hostler_profile")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="managed_hostlers")
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="hostlers")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name="hostlers")
    phone = models.CharField(max_length=15)
    check_in_date = models.DateField()
    check_out_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    parent_number= models.CharField(max_length=15, blank=True, null=True)
    # fees= models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    joining_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hostel.name}"

MEAL_TYPES = [
    ('BRK', 'Breakfast'),
    ('LNC', 'Lunch'),
    ('DIN', 'Dinner'),
]

class MealTemplate(models.Model):
    """ Pre-defined meals created by the system or owner """
    name = models.CharField(max_length=100)
    default_meal_type = models.CharField(max_length=3, choices=MEAL_TYPES)
    hostel= models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name="meal_templates")
    is_deleted= models.BooleanField(default=False)  # Soft delete flag
    def __str__(self):
        return self.name


class AssignedMeal(models.Model):
    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.CASCADE,
        related_name="assigned_meals"
    )
    date = models.DateField(default=timezone.now)
    meal_type = models.CharField(
        max_length=3,
        choices=MEAL_TYPES
    )
    meal_item = models.ForeignKey(
        MealTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_meals"
    )
    amount_per_hostler = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    meal_image = models.ImageField(
        upload_to="meal_images/",
        blank=True,
        null=True
    )
    description = models.TextField(blank=True, null=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_meals",
        blank=True
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="disliked_meals",
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ("hostel", "date", "meal_type")
        ordering = ["-date", "meal_type"]

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_dislikes(self):
        return self.dislikes.count()

    def __str__(self):
        return f"{self.hostel.name} - {self.date} - {self.get_meal_type_display()}"
    
class MessCharge(models.Model):
    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.CASCADE,
        related_name="monthly_bills"
    )

    hostler = models.ForeignKey(
        Hostler,
        on_delete=models.CASCADE,
        related_name="mess_charges"
    )

    assigned_meal = models.ForeignKey(
        AssignedMeal,
        on_delete=models.CASCADE,
        related_name="charges"
    )
    date = models.DateField()
    meal_type = models.CharField(
        max_length=3,
        choices=MEAL_TYPES
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    is_paid = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("hostler", "assigned_meal")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.hostler} - {self.get_meal_type_display()} - ₹{self.amount}"
    

class MonthlyMessBill(models.Model):
    hostel = models.ForeignKey(
        Hostel,
        on_delete=models.CASCADE,
        related_name="monthly_charges"
    )
    hostler = models.ForeignKey(
        Hostler,
        on_delete=models.CASCADE,
        related_name="monthly_mess_bills"
    )
    month = models.IntegerField()
    year = models.IntegerField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("hostler", "month", "year")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.hostler} - {self.month}/{self.year} - ₹{self.total_amount}"



class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    ]
    hostler = models.ForeignKey(Hostler, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    billing_date = models.DateField(auto_now_add=True) 
    due_date = models.DateField(null=True, blank=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    def save(self, *args, **kwargs):
        if not self.due_date:
            # Deadline is 30 days from the bill generation
            self.due_date = timezone.now().date() + timedelta(days=30)
        super().save(*args, **kwargs)


class OwnerSubscription(models.Model):

    PLAN_CHOICES = (
        ("FREE", "Free"),
        ("PRO", "Pro"),
        ("PREMIUM", "Premium"),
    )

    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="subscription"
    )

    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default="FREE"
    )

    hostel_limit = models.IntegerField(default=1)

    is_active = models.BooleanField(default=True)

    start_date = models.DateTimeField(auto_now_add=True)

    end_date = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.username} - {self.plan}"