from rest_framework import serializers

from Base_Panel.models import Hostel,Hostler
from App.models import User


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
