from rest_framework import serializers

from Base_Panel.models import Hostel,Hostler
from App.models import User
from Base_Panel.models import Transaction

from datetime import date

from dateutil.relativedelta import relativedelta

from Base_Panel.models import Room,Room_image

class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = ['id', 'name', 'address', 'city', 'state']


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class HostlerViewSerializer(serializers.ModelSerializer):

    hostel = HostelSerializer(read_only=True)
    owner = OwnerSerializer(read_only=True)

    class Meta:
        model = Hostler
        fields = '__all__'


class HostelViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__'


class payment_serilizer(serializers.ModelSerializer):

    next_payment_date =serializers.SerializerMethodField()

    days_left =serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = '__all__'
        depth = 1

    # NEXT PAYMENT DATE

    def get_next_payment_date(
        self,
        obj
    ):
        if obj.hostler.joining_date:
            today = date.today()
            joining_date = (
                obj.hostler.joining_date
            )
            months_stayed = (
                (today.year - joining_date.year) * 12
                + today.month
                - joining_date.month
            )
            next_payment = (
                joining_date
                + relativedelta(
                    months=months_stayed + 1
                )
            )
            return next_payment
        return None

    # DAYS LEFT
    def get_days_left(
        self,
        obj
    ):
        if obj.hostler.joining_date:
            today = date.today()
            joining_date = (
                obj.hostler.joining_date
            )
            months_stayed = (
                (today.year - joining_date.year) * 12
                + today.month
                - joining_date.month
            )
            next_payment = (
                joining_date
                + relativedelta(
                    months=months_stayed + 1
                )
            )
            return (
                next_payment - today
            ).days
        return 0
    

class RoommateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")

    class Meta:
        model = Hostler
        fields = [
            "id",
            "username",
            "phone",
            "monthly_rent",
        ]


class RoomImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Room_image
        fields = ["id", "image"]
      

class Room_Serializer(serializers.ModelSerializer):
    roommates = serializers.SerializerMethodField()
    images= RoomImageSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = "__all__"

    def get_roommates(self, obj):
        hostlers = obj.hostlers.all()
        return RoommateSerializer(hostlers, many=True).data
    
class HostlerRoomSerializer(serializers.ModelSerializer):
    room = Room_Serializer(read_only=True)

    class Meta:
        model = Hostler
        fields = "__all__"