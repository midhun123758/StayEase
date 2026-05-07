from rest_framework import serializers
from .models import Hostel,Hostler,Room
from .models import User

class HostelSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    class Meta:
        model = Hostel
        fields = ['id', 'owner', 'name', 'address', 'location', 'latitude', 'longitude', 'city', 'state', 'description'] 


class HostlerCreateSerializer(serializers.ModelSerializer):
    hostel = serializers.PrimaryKeyRelatedField(queryset=Hostel.objects.none())
    room = serializers.PrimaryKeyRelatedField(
        queryset=Room.objects.none(),
        required=False,
        allow_null=True
    )

    phone = serializers.CharField()
    parent_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    check_in_date = serializers.DateField()
    check_out_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "hostel",
            "room",
            "phone",
            "parent_number",
            "check_in_date",
            "check_out_date",
        ]
        read_only_fields = ["id"]

    # 🔥 Only show owner’s hostels & rooms
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

        hostel = validated_data.pop("hostel")
        room = validated_data.pop("room", None)
        phone = validated_data.pop("phone")
        parent_number = validated_data.pop("parent_number", None)
        check_in_date = validated_data.pop("check_in_date")
        check_out_date = validated_data.pop("check_out_date", None)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=None,
            role="hostler",
            owner=owner,
        )

        user.set_unusable_password()
        user.save()


        Hostler.objects.create(
            user=user,
            owner=owner,
            hostel=hostel,
            room=room,
            phone=phone,
            parent_number=parent_number,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
        )

        return user
class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'room_number', 'room_type', 'price', 'is_available']
        read_only_fields = ['id']
        
class HostlerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    hostel_name = serializers.CharField(source="hostel.name", read_only=True)
    room_number = serializers.CharField(source="room.room_number", read_only=True, allow_null=True)

    class Meta:
        model = Hostler
        fields = [
            "id",
            "username",
            "email",
            "hostel",
            "hostel_name",
            "room",
            "room_number",
            "phone",
            "parent_number",
            "check_in_date",
            "check_out_date",
            "is_active",
        ]