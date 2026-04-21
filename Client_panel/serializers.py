from rest_framework import serializers
from Base_Panel.models import Hostel

class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = ['id', 'name', 'latitude', 'longitude', 'city', 'state', 'description', 'rooms_available']
        read_only_fields = ['id']


