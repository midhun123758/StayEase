from Base_Panel.models import HostelDocument
from rest_framework import serializers

class HostelDocumentSerializer(serializers.ModelSerializer):

    owner_name = serializers.CharField(
        source="uploaded_by.username",
        read_only=True
    )

    owner_email = serializers.CharField(
        source="uploaded_by.email",
        read_only=True
    )

    kyc_completed = serializers.BooleanField(
        source="uploaded_by.kyc_completed",
        read_only=True
    )

    hostel_name = serializers.CharField(
        source="hostel.name",
        read_only=True
    )

    class Meta:

        model = HostelDocument

        fields = [
            "id",
            "owner_name",
            "owner_email",
            "hostel_name",
            "document_type",
            "file_url",
            "uploaded_at",
            "kyc_completed"
        ]