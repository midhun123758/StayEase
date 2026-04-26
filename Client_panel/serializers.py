from rest_framework import serializers
from Base_Panel.models import Hostel
from App.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
class HostelSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    class Meta:
        model = Hostel
        fields = ['id','owner', 'name', 'latitude', 'longitude', 'city', 'state', 'description', 'rooms_available']
        read_only_fields = ['id']


