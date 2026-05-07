from django.contrib.auth import authenticate
from .models import  KycDocument, User, PasswordResetOTP
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import KYCSerializer, Profile
import requests
from .models import PasswordResetOTP
from .serializer import sendOTpSerilaizer, verifyOTPSerilaizer, ResetPasswordSerializer
import random
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAuthenticated
# 🔐 LOGIN VIEW
class login_view(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        captcha = request.data.get('captcha')  # ✅ get captcha

        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

      
        if not captcha:
            return Response(
                {'error': 'CAPTCHA is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not verify_captcha(captcha):
            return Response(
                {'error': 'Invalid CAPTCHA'},
                status=status.HTTP_400_BAD_REQUEST
            )

        
        user_obj = User.objects.filter(email=email).first()

        if not user_obj:
            return Response({'error': 'User not found'}, status=404)

        if user_obj.is_google_user:
            return Response(
                {'error': 'This account uses Google login'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔐 Authenticate
        user = authenticate(username=user_obj.username, password=password)

        if not user:
            return Response({'error': 'Invalid credentials'}, status=401)

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'owner_id': user.owner.id if user.owner else None,
                'is_google_user': user.is_google_user,
                'kyc_completed': user.kyc_completed
            }
        })

class logout_view(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)     
# 📝 SIGNUP VIEW
class signup_view(APIView):
    def post(self, request):
        serializer = Profile(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_google_user': user.is_google_user,
                'kyc_completed': user.kyc_completed
            }, status=201)
        return Response(serializer.errors, status=400)


# 👑 OWNER SIGNUP
class OwnerSignupView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not email or not password:
            return Response(
                {"error": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.role = "owner"
        user.is_staff = True
        user.save()

        return Response({
            "message": "Owner account created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_google_user": user.is_google_user,
                "kyc_completed": user.kyc_completed

            }
        }, status=status.HTTP_201_CREATED)


# 🔥 GOOGLE LOGIN VIEW
class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("token")

        # 🚨 Validate token exists
        if not token:
            return Response(
                {"error": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔒 Verify token with Google
        google_response = requests.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
        )

        if google_response.status_code != 200:
            return Response(
                {"error": "Invalid Google token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        google_data = google_response.json()

        # 🔒 Check email verified
        if not google_data.get("email_verified"):
            return Response(
                {"error": "Email not verified"},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = google_data.get("email")
        username = google_data.get("name") or email.split("@")[0]

        if not email:
            return Response(
                {"error": "Email not found from Google"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔥 Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "is_google_user": True
            }
        )

        # 🔄 Ensure flag is correct
        if not user.is_google_user:
            user.is_google_user = True
            user.save()

        # 🔑 Generate JWT
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "owner_id": user.owner.id if user.owner else None,
                "is_google_user": user.is_google_user,
                "kyc_completed": user.kyc_completed

            },
        })


class sendotpView(APIView):
    def post(self,request):
        serialiser=sendOTpSerilaizer(data=request.data)
        serialiser.is_valid(raise_exception=True)
        
        email=serialiser.validated_data['email']
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            return Response ({"error": "Email not registered"}, status=400)

        otp = str(random.randint(100000, 999999))
        PasswordResetOTP.objects.filter(user=user).delete()

        PasswordResetOTP.objects.create(
            user=user,
            otp=otp
        )

        send_mail(
            "Password Reset OTP",
            f"Your OTP is {otp}. Valid for 5 minutes.",
            "noreply@example.com",
            [email],
        )

        return Response({"message": "OTP sent successfully"}, status=200)
    
from datetime import timedelta
from django.utils import timezone

class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        otp_obj = PasswordResetOTP.objects.filter(
            user=user,
            otp=otp
        ).order_by('-created_at').first()  # ✅ latest OTP

        if not otp_obj:
            return Response({"error": "Invalid OTP"}, status=400)

        if otp_obj.is_expired():
            otp_obj.delete()
            return Response({"error": "OTP expired"}, status=400)

        otp_obj.is_verified = True
        otp_obj.save()

        return Response({"message": "OTP verified"})

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        # Get data from frontend
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        # Validate fields
        if not email or not new_password or not confirm_password:
            return Response(
                {"error": "Email and password are required"},
                status=400
            )

        # Check password match
        if new_password != confirm_password:
            return Response(
                {"error": "Passwords do not match"},
                status=400
            )

        try:
            # Find user
            user = User.objects.get(email__iexact=email)

            # Check verified OTP
            otp_obj = PasswordResetOTP.objects.get(
                user=user,
                is_verified=True
            )

            # Set new password (hashed securely)
            user.set_password(new_password)

            # Activate account if inactive
            user.is_active = True

            # Remove google-only restriction if exists
            if hasattr(user, "is_google_user"):
                user.is_google_user = False

            user.save()

            # Delete used OTP
            otp_obj.delete()

            return Response(
                {"message": "Password reset successful"},
                status=200
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=404
            )

        except PasswordResetOTP.DoesNotExist:
            return Response(
                {"error": "OTP not verified"},
                status=400
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=500
            )
def verify_captcha(token):
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': token
    }
    response = requests.post(url, data=data)
    return response.json().get("success", False)

class KYCView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # 🔹 Prevent duplicate KYC
        if hasattr(user, "kycdocument"):
            return Response(
                {"error": "KYC already submitted"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = KYCSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(user=user)

            user.kyc_completed = True
            user.save()

            return Response(
                {"message": "KYC submitted successfully. Waiting for approval."},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=400)