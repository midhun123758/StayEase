from rest_framework import serializers
from .models import Hostel


class HostelSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    class Meta:
        model = Hostel
        fields = ['id', 'owner', 'name', 'address', 'location', 'latitude', 'longitude', 'city', 'state', 'description'] 