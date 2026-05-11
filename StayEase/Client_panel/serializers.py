from rest_framework import serializers
from Base_Panel.models import Hostel
from App.models import User
from .models import Enquiry
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


class EnquirySerializer(serializers.ModelSerializer):
    hostel_name = serializers.ReadOnlyField(source='hostel.name')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_at = serializers.DateTimeField(format="%d %b %Y", read_only=True)

    class Meta:
        model = Enquiry
        fields = [
            'id', 'user', 'hostel', 'hostel_name', 'full_name', 
            'email', 'phone', 'preferred_date', 'stay_months', 
            'message', 'status', 'status_display', 'rejection_reason', 
            'created_at'
        ]
        read_only_fields = ['user', 'status', 'rejection_reason']

    def validate_stay_months(self, value):
        if value < 1:
            raise serializers.ValidationError("Stay duration must be at least 1 month.")
        return value