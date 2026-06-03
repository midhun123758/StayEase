
from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers
from .models import AssignedMeal, Hostel, HostelFeedback,Hostler, MealTemplate, MessCharge,Room, Room_image, Subscription_Amount, Transaction
from .models import User
from django.db.models import Sum
from Client_panel.models import Enquiry 
class HostelSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    class Meta:
        model = Hostel
        fields = ['id', 'owner', 'name', 'address', 'location', 'latitude', 'longitude', 'city', 'state', 'description','rooms_available','mess_service','contact_number','image1','image2','image3','image4'] 


class HostlerCreateSerializer(serializers.ModelSerializer):
    hostel = serializers.PrimaryKeyRelatedField(queryset=Hostel.objects.none())
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.none(),
        required=False,
        allow_null=True
    )
    
    # Required for payment logic and fixing IntegrityError
    monthly_rent = serializers.DecimalField(max_digits=10, decimal_places=2, write_only=True)
    
    phone = serializers.CharField()
    parent_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "hostel", "room", 
            "monthly_rent", "phone", "parent_number", 
            "check_in_date", "check_out_date",
        ]
        read_only_fields = ["id"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request:
            owner = request.user
            self.fields["hostel"].queryset = Hostel.objects.filter(owner=owner)
            self.fields["room"].queryset = Room.objects.filter(hostel__owner=owner)

    def validate(self, data):
        request = self.context["request"]
        owner = request.user
        hostel = data.get("hostel")
        room = data.get("room")

        if hostel.owner != owner:
            raise serializers.ValidationError("You can only assign your own hostel.")
        if room and room.hostel != hostel:
            raise serializers.ValidationError("Room does not belong to selected hostel.")
        return data

    def create(self, validated_data):
        request = self.context["request"]
        owner = request.user

        # Extract data before creating User
        hostel = validated_data.pop("hostel")
        room = validated_data.pop("room", None)
        monthly_rent = validated_data.pop("monthly_rent")
        phone = validated_data.pop("phone")
        parent_number = validated_data.pop("parent_number", None)
        check_in_date = validated_data.pop("check_in_date")
        check_out_date = validated_data.pop("check_out_date", None)

        # 1. Create User
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=None,
            role="hostler",
            owner=owner,
        )
        user.set_unusable_password()
        user.save()

        # 2. Create Hostler (monthly_rent here fixes the IntegrityError)
        Hostler.objects.create(
            user=user,
            owner=owner,
            hostel=hostel,
            room=room,
            monthly_rent=monthly_rent,
            phone=phone,
            parent_number=parent_number,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
        )

        return user

class HostlerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True, allow_null=True)

    class Meta:
        model = Hostler
        fields = [
            "id", "username", "email", "hostel", "hostel_name", 
            "room", "room_number", "phone", "parent_number", 
            "check_in_date", "check_out_date", "is_active",
            "monthly_rent", "joining_date"
        ]
# class RoomSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Room
#         fields = ['id', 'room_number', 'room_type', 'price', 'is_available']
#         read_only_fields = ['id']

class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room_image
        fields = ['id', 'image','room']
class RoomSerializer(serializers.ModelSerializer):
    hostlers = HostlerSerializer(many=True, read_only=True)
    images = RoomImageSerializer(many=True, read_only=True)
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'price', 'is_available', 'hostlers','bed_space','images']
        read_only_fields = ['id']

class EnquirySerializer(serializers.ModelSerializer):
    # These fields pull data from the related models for easy display
    hostel_name = serializers.ReadOnlyField(source='hostel.name')
    # get_status_display returns 'Pending' instead of 'pending'
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    # Formats the date to a readable string (e.g., "08 May 2026")
    created_at = serializers.DateTimeField(format="%d %b %Y", read_only=True)

    class Meta:
        model = Enquiry
        fields = [
            'id',
            'full_name',
            'email',
            'phone',
            'preferred_date',
            'stay_months',
            'message',
            'status',
            'status_display',
            'hostel',
            'hostel_name',
            'created_at',
            'updated_at',
            'rejection_reason'
        ]

class MealTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MealTemplate
        fields = ['id', 'name', 'default_meal_type', 'hostel']

class AssignedMealSerializer(serializers.ModelSerializer):
    # This shows the meal name in the response so the frontend doesn't just see an ID
    meal_name = serializers.CharField(source='meal_item.name', read_only=True)
    
    class Meta:
        model = AssignedMeal
        fields = ['id', 'hostel', 'date', 'meal_type', 'meal_item', 'meal_name', 'total_likes', 'total_dislikes',]


class TransactionSerializer(serializers.ModelSerializer):

    days_until_due = serializers.SerializerMethodField()

    mess_total = serializers.SerializerMethodField()

    total_payable = serializers.SerializerMethodField()

    class Meta:
        model = Transaction

        fields = [
            'id',
            'amount',
            'billing_date',
            'due_date',
            'status',
            'days_until_due',
            'mess_total',
            'total_payable',
        ]


    def get_days_until_due(self, obj):

        remaining = (
            obj.due_date -
            timezone.now().date()
        ).days

        return max(0, remaining)


    def get_mess_total(self, obj):

        mess_total = MessCharge.objects.filter(
            hostler=obj.hostler,
            is_paid=False
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        return mess_total


    def get_total_payable(self, obj):

        mess_total = MessCharge.objects.filter(
            hostler=obj.hostler,
            is_paid=False
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

        return float(obj.amount) + float(mess_total)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_google_user', 'kyc_completed']
        read_only_fields = ['id', 'role', 'is_google_user', 'kyc_completed']



class SubscriptionAmountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription_Amount
        fields = "__all__"

# Base_Panel/serializers.py

class HostelFeedbackSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = HostelFeedback

        fields = [
            "id",
            "hostel",
            "user",
            "username",
            "rating",
            "review",
            "image",
            "owner_reply",
            "created_at"
        ]

        read_only_fields = [
            "user",
            "owner_reply"
        ]

class HostlerCheckoutSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    reason = serializers.CharField(required=False, allow_blank=True, default="")


# serializers.py

class CollectPaymentSerializer(serializers.Serializer):

    transaction_id = serializers.IntegerField()

    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_method = serializers.ChoiceField(
        choices=[
            "cash",
            "gpay",
            "phonepe",
            "paytm",
            "bank"
        ]
    )
    payment_note = serializers.CharField(
        required=False,
        allow_blank=True
    )

class CheckoutSettlementSerializer(

    serializers.Serializer
):

    PAYMENT_METHODS = [

        ("cash", "Cash"),

        ("gpay", "Google Pay"),

        ("phonepe", "PhonePe"),

        ("paytm", "Paytm"),

        ("bank", "Bank Transfer"),
    ]

    settlement_id = serializers.IntegerField()

    amount = serializers.DecimalField(

        max_digits=10,

        decimal_places=2,

        min_value=Decimal("0.01")
    )

    payment_method = serializers.ChoiceField(

        choices=PAYMENT_METHODS
    )

    payment_note = serializers.CharField(

        required=False,

        allow_blank=True,

        max_length=255
    )