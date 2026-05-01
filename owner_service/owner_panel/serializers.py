from rest_framework import serializers
from .models import Hostel


class HostelSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    owner_user_id = serializers.IntegerField(read_only=True) # Mark owner_user_id as read-only for input validation

    class Meta:
        model = Hostel
        fields = "__all__"

    def get_owner(self, obj):
        from grpc_files.user_client import get_user_from_grpc
        return get_user_from_grpc(obj.owner_user_id)