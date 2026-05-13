
from django.utils import timezone
from django.shortcuts import render
from rest_framework import status
from App.models import User
from .models import AssignedMeal, ChatRoom, Hostel, HostelDocument, Hostler, MealTemplate, MessCharge, Room_image, Transaction
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response            
from .serilalizers import AssignedMealSerializer, EnquirySerializer, HostelSerializer, HostlerCreateSerializer, HostlerSerializer, RoomImageSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from .utils.s3 import generate_presigned_url
from .models import Room
from .serilalizers import RoomSerializer ,MealTemplateSerializer  
from Client_panel.models import Enquiry
from django.db import transaction
from django.db.models import Sum, Q
from rest_framework.parsers import MultiPartParser,FormParser
from .models import OwnerSubscription
class HostelListView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # GET OWNER SUBSCRIPTION
        subscription, created = OwnerSubscription.objects.get_or_create(
            owner=request.user,
            defaults={
                "plan": "FREE",
                "hostel_limit": 1
            }
        )
        # CURRENT HOSTEL COUNT
        hostel_count = Hostel.objects.filter(
            owner=request.user
        ).count()
        # CHECK LIMIT
        if hostel_count >= subscription.hostel_limit:

            return Response(
                {
                    "error": "Hostel limit reached",
                    "current_plan": subscription.plan,
                    "hostel_limit": subscription.hostel_limit,
                    "current_hostels": hostel_count,
                    "message": "Upgrade your subscription to add more hostels"
                },
                status=403
            )
        serializer = HostelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(
                {
                    "message": "Hostel created successfully",
                    "data": serializer.data
                },
                status=201
            )
        return Response(serializer.errors, status=400)

    def get(self, request):

        hostels = Hostel.objects.filter(
            owner=request.user
        ).order_by("-created_at")

        serializer = HostelSerializer(
            hostels,
            many=True
        )

        return Response(serializer.data)
class AddHostlerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        room_id = request.data.get("room")
        monthly_rent = request.data.get("monthly_rent")

        if not monthly_rent:
            return Response({"error": "Monthly rent is required."}, status=400)

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({"error": "Room not found"}, status=404)

        current_hostlers = Hostler.objects.filter(room=room).count()
        if current_hostlers >= room.bed_space:
            return Response({"error": "This room is already full."}, status=400)

        try:
            with transaction.atomic():
                serializer = HostlerCreateSerializer(
                    data=request.data,
                    context={"request": request}
                )

                if serializer.is_valid():
                    user = serializer.save()
                    
                    hostler = Hostler.objects.get(user=user)
                    hostler.monthly_rent = monthly_rent
                    hostler.save()

                    Transaction.objects.create(
                        hostler=hostler,
                        amount=monthly_rent,
                        status='pending',
                        billing_date=timezone.now().date()
                    )

                    response_serializer = HostlerSerializer(hostler)
                    return Response(response_serializer.data, status=201)
                
                return Response(serializer.errors, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

class GenerateUploadURL(APIView):
    def post(self, request):
        file_type = request.data.get("file_type")

        upload_url, file_url = generate_presigned_url(file_type)

        return Response({
            "upload_url": upload_url,
            "file_url": file_url
        })
    
class AddDocument(APIView):
    def post(self, request):
        HostelDocument.objects.create(
            hostel_id=request.data.get("hostel"),
            uploaded_by=request.user,
            file_url=request.data.get("file_url"),
            document_type=request.data.get("document_type")
        )
        return Response({"message": "Saved"})
    



class my_hostlers(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        hostel_id=request.GET.get("hostel_id")
        hostlers = (
            Hostler.objects
            .filter(owner=request.user, is_active=True, hostel_id=hostel_id)
            .select_related("user", "hostel", "room")
        )
        serializer = HostlerSerializer(hostlers, many=True)
        return Response(serializer.data, status=200)
    



class AddRoomView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        hostel_id = request.GET.get("hostel_id")

        # 1. Ownership check
        try:
            hostel = Hostel.objects.get(id=hostel_id, owner=request.user)
        except Hostel.DoesNotExist:
            return Response({"error": "Hostel not found or unauthorized"}, status=404)

        # 2. Validate and Save Room
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                room = serializer.save(hostel=hostel)
                images = request.FILES.getlist("images")
                for img in images:
                    Room_image.objects.create(
                        room=room,
                        image=img
                    )

            return Response({
                "message": "Room created successfully with images",
                "room": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Room_listView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        hostel_id=request.GET.get("hostel_id")
        rooms= Room.objects.filter(hostel__owner=request.user, hostel_id=hostel_id)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    

class EnquiryListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        hostel_id=request.GET.get("hostel_id")
        enqueries = Enquiry.objects.filter(hostel__owner=request.user,hostel_id=hostel_id)
        serializer = EnquirySerializer(enqueries, many=True)
        return Response(serializer.data)
# views.py
class OwnerChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hostel_id = request.GET.get("hostel_id")
        if not hostel_id:
            return Response(
                {"error": "Hostel ID required"},
                status=400
            )
        rooms = (
            ChatRoom.objects
            .filter(
                owner=request.user,
                hostel_id=hostel_id,
                hostel__owner=request.user
            )
            .select_related("client", "hostel")
            .prefetch_related("messages")
        )
        data = [
            {
                "id": r.id,
                "client": r.client.id,
                "client_username": r.client.username,
                "hostel": r.hostel.id,
                "hostel_name": r.hostel.name,
                "last_message_preview": (
                    r.messages.last().message
                    if r.messages.exists()
                    else ""
                ),
            }
            for r in rooms
        ]
        return Response(data, status=200)
    
class DailyMealAssignmentView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        hostel_id = request.data.get("hostel")
        meal_item_id = request.data.get("meal_item")
        date = request.data.get("date")
        meal_type = request.data.get("meal_type")

        amount_per_hostler = request.data.get("amount_per_hostler")
        description = request.data.get("description")
        meal_image = request.FILES.get("meal_image")

        if not hostel_id or not meal_item_id or not date or not meal_type:
            return Response(
                {
                    "error": "hostel, meal_item, date and meal_type are required"
                },
                status=400
            )

        try:
            hostel = Hostel.objects.get(
                id=hostel_id,
                owner=request.user
            )

            meal_item = MealTemplate.objects.get(
                id=meal_item_id,
                hostel=hostel,
                is_deleted=False
            )

            assignment, created = AssignedMeal.objects.update_or_create(
                hostel=hostel,
                date=date,
                meal_type=meal_type,
                defaults={
                    "meal_item": meal_item,
                    "amount_per_hostler": amount_per_hostler or 0,
                    "description": description,
                    "meal_image": meal_image,
                }
            )

            # CREATE / UPDATE MESS CHARGES
            hostlers = Hostler.objects.filter(
                hostel=hostel,
                is_active=True
            )

            for hostler in hostlers:

                MessCharge.objects.update_or_create(
                    hostler=hostler,
                    assigned_meal=assignment,
                    defaults={
                        "hostel": hostel,  # FIXED
                        "date": assignment.date,
                        "meal_type": assignment.meal_type,
                        "amount": assignment.amount_per_hostler,
                    }
                )

            serializer = AssignedMealSerializer(assignment)

            return Response(
                serializer.data,
                status=201 if created else 200
            )

        except Hostel.DoesNotExist:
            return Response(
                {"error": "Hostel not found or unauthorized"},
                status=404
            )

        except MealTemplate.DoesNotExist:
            return Response(
                {"error": "Meal item not found"},
                status=404
            )

    def get(self, request):

        hostel_id = request.query_params.get("hostel")
        date = request.query_params.get("date")

        if not hostel_id or not date:
            return Response(
                {"error": "hostel and date are required"},
                status=400
            )

        try:
            hostel = Hostel.objects.get(
                id=hostel_id,
                owner=request.user
            )

        except Hostel.DoesNotExist:
            return Response(
                {"error": "Hostel not found"},
                status=404
            )

        assignments = AssignedMeal.objects.filter(
            hostel=hostel,
            date=date
        ).select_related(
            "meal_item"
        )

        serializer = AssignedMealSerializer(
            assignments,
            many=True
        )

        return Response(serializer.data, status=200)

class Meal_assignmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        hostel_id = request.data.get("hostel")

        if not hostel_id:
            return Response(
                {"error": "Hostel ID is required"},
                status=400
            )

        try:
            hostel = Hostel.objects.get(
                id=hostel_id,
                owner=request.user
            )

        except Hostel.DoesNotExist:
            return Response(
                {"error": "Hostel not found"},
                status=404
            )

        serializer = MealTemplateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(hostel=hostel)

            return Response(
                serializer.data,
                status=201
            )

        return Response(serializer.errors, status=400)

    def get(self, request):

        hostel_id = request.query_params.get("hostel")

        if not hostel_id:
            return Response(
                {"error": "Hostel ID is required"},
                status=400
            )

        try:
            hostel = Hostel.objects.get(
                id=hostel_id,
                owner=request.user
            )

        except Hostel.DoesNotExist:
            return Response(
                {"error": "Hostel not found"},
                status=404
            )

        meals = MealTemplate.objects.filter(
            hostel=hostel,
            is_deleted=False
        )

        serializer = MealTemplateSerializer(
            meals,
            many=True
        )

        return Response(serializer.data, status=200)

    def delete(self, request):

        meal_id = request.data.get("meal_id")
        hostel_id = request.data.get("hostel")

        if not meal_id or not hostel_id:
            return Response(
                {
                    "error": "meal_id and hostel are required"
                },
                status=400
            )

        try:
            meal = MealTemplate.objects.get(
                id=meal_id,
                hostel_id=hostel_id,
                hostel__owner=request.user
            )

            meal.is_deleted = True
            meal.save()

            return Response(
                {"message": "Meal template deleted"},
                status=200
            )

        except MealTemplate.DoesNotExist:
            return Response(
                {"error": "Meal template not found"},
                status=404
            )





class Enquery_change_view(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, enquiry_id):
        status_value = request.data.get("status")
        reason = request.data.get("rejection_reason")
        
        allowed_status = ['pending', 'responded', 'closed', 'accepted by owner', 'rejected']
        
        if status_value not in allowed_status:
            return Response({"error": f"Invalid status. Must be one of: {allowed_status}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            enquiry = Enquiry.objects.get(
                id=enquiry_id,
                hostel__owner=request.user
            )
        except Enquiry.DoesNotExist:
            return Response({"error": "Enquiry not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        if status_value == 'rejected':
            if not reason or len(reason.strip()) < 5:
                return Response({"error": "A valid rejection reason (min 5 chars) is required."}, status=status.HTTP_400_BAD_REQUEST)
            enquiry.rejection_reason = reason
        else:
            enquiry.rejection_reason = None

        # 5. Save and Return
        enquiry.status = status_value
        enquiry.save()

        return Response({
            "message": f"Enquiry marked as {status_value}",
            "status": enquiry.status,
            "rejection_reason": enquiry.rejection_reason
        }, status=status.HTTP_200_OK)

class FinancialOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        owner = request.user
        hostel_id = request.GET.get("hostel")

        if not hostel_id:
            return Response({"error": "Hostel ID required"}, status=400)

        transactions = Transaction.objects.filter(
            hostler__owner=owner,
            hostler__hostel_id=hostel_id
        )

        stats = transactions.aggregate(
            total_pending=Sum("amount", filter=Q(status="pending")),
            total_collected=Sum("amount", filter=Q(status="paid")),
        )

        pending_hostlers = (
            Hostler.objects
            .filter(
                owner=owner,
                hostel_id=hostel_id,
                transactions__status="pending"
            )
            .annotate(
                total_due=Sum(
                    "transactions__amount",
                    filter=Q(transactions__status="pending")
                )
            )
            .select_related("user", "room")
            .distinct()
        )

        hostler_dues = [
            {
                "name": h.user.username,
                "room": h.room.room_number if h.room else "N/A",
                "amount_due": h.total_due or 0,
                "phone": h.phone,
            }
            for h in pending_hostlers
        ]

        pending = stats["total_pending"] or 0
        collected = stats["total_collected"] or 0

        return Response({
            "summary": {
                "pending": pending,
                "collected": collected,
                "total_expected": pending + collected,
            },
            "payable_list": hostler_dues,
        }, status=200)

class RoomImagesListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        hostel_id = request.GET.get("hostel")
        # VALIDATION
        if not hostel_id:
            return Response(
                {"error": "Hostel ID required"},
                status=400
            )
        images = (
            Room_image.objects
            .filter(
                room__hostel__owner=request.user,
                room__hostel_id=hostel_id
            )
            .select_related(
                "room",
                "room__hostel"
            )
        )
        serializer = RoomImageSerializer(images, many=True)

        return Response(serializer.data, status=200)
    


class Edit_hostel(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        hostel_id = request.GET.get("hostel_id")

        if not hostel_id:
            return Response(
                {"error": "Hostel ID is required"},
                status=400
            )
        try:
            hostel_data = Hostel.objects.get(
                id=hostel_id,
                owner=request.user
            )
        except Hostel.DoesNotExist:
            return Response(
                {"error": "Hostel not found or unauthorized"},
                status=404
            )
        serializer = HostelSerializer(
            hostel_data,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

class Owner_Profile(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        owner_id = request.GET.get("id")
        if not owner_id:
            return Response(
                {"error": "Owner id is required"},
                status=400
            )
        try:
            owner = User.objects.get(
                id=owner_id,
                role="owner"
            )
        except User.DoesNotExist:
            return Response(
                {"error": "Owner not found"},
                status=404
            )
        serializer = UserSerializer(owner)

        return Response(serializer.data, status=200)