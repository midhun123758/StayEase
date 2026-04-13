from django.contrib.auth import authenticate
from .models import User
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializer import Profile


class login_view(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user_obj = User.objects.filter(email=email).first()

        if not user_obj:
            return Response({'error': 'User not found'}, status=404)

        # 🔥 If Google user → block password login
        if user_obj.is_google_user:
            return Response({
                'error': 'This account uses Google login'
            }, status=400)

        # 🔹 Authenticate
        user = authenticate(username=user_obj.username, password=password)

        if user:
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
                    'is_google_user': user.is_google_user
                }
            })

        return Response({'error': 'Invalid credentials'}, status=401)
    
class signup_view(APIView):
    def post(self, request):
        serializer = Profile(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }, status=201)

        return Response(serializer.errors, status=400)
    
class OwnerSignupView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        # 🔒 Check required fields
        if not username or not email or not password:
            return Response(
                {"error": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔒 Prevent duplicate email
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 🔥 Create OWNER directly
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.role = "owner"
        user.is_staff = True   # optional (for admin panel)
        user.save()

        return Response({
            "message": "Owner account created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)