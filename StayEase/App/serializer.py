from rest_framework import serializers
from .models import KycDocument, User


class Profile(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password','role','upi_id']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'user')
        )
        return user
    
class sendOTpSerilaizer(serializers.Serializer):
    email=serializers.EmailField()

class verifyOTPSerilaizer(serializers.Serializer):
    email=serializers.EmailField()
    otp=serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)

class KYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = KycDocument
        fields = [
            "full_name",
            "phone",
            "address",
            "latitude",
            "longitude",
            "id_proof",
        ]

    def validate(self, data):
        # 🔹 Required fields
        required_fields = [
            "full_name",
            "phone",
            "address",
            "latitude",
            "longitude",
            "id_proof",
        ]

        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(
                    {field: f"{field.replace('_', ' ').capitalize()} is required"}
                )

        return data