from rest_framework import serializers
from .models import Hostel
from .models import User

class HostelSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    class Meta:
        model = Hostel
        fields = ['id', 'owner', 'name', 'address', 'location', 'latitude', 'longitude', 'city', 'state', 'description'] 



class HostlerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "owner"]
        read_only_fields = ["id", "role", "owner"]

    def create(self, validated_data):
        owner = self.context["request"].user
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role="hostler",
            owner=owner
        )

        return user