
from django.utils import timezone
from django.shortcuts import render
from rest_framework import status
from App.models import User
from .models import AssignedMeal, ChatRoom, Hostel, HostelDocument, Hostler, MealTemplate, MessCharge, Room_image, Subscription_Amount, Transaction
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response            
from .serilalizers import AssignedMealSerializer, EnquirySerializer, HostelSerializer, HostlerCreateSerializer, HostlerSerializer, RoomImageSerializer, SubscriptionAmountSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from .utils.s3 import generate_presigned_url
from .models import Room
from .serilalizers import RoomSerializer ,MealTemplateSerializer  
from Client_panel.models import Enquiry
from django.db import transaction
from django.db.models import Sum, Q
from rest_framework.parsers import MultiPartParser,FormParser
from .models import OwnerSubscription
import razorpay
from django.conf import settings
from Client_panel.utils import send_client_notification


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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            hostel = Hostel.objects.get(owner=request.user)
            document = HostelDocument.objects.create(
                hostel=hostel,
                uploaded_by=request.user,
                file_url=request.data.get("file_url"),
                document_type=request.data.get("document_type")
            )
            return Response({
                "message": "Saved Successfully",
                "document_id": document.id
            }, status=status.HTTP_201_CREATED)

        except Hostel.DoesNotExist:
            return Response({
                "error": "Hostel not found for this owner"
            }, status=status.HTTP_404_NOT_FOUND)


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
        reason = request.data.get("rejection_reason", "")

        allowed_status = [
            "pending",
            "responded",
            "closed",
            "accepted by owner",
            "rejected",
        ]

        if not status_value:
            return Response(
                {"error": "Status is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if status_value not in allowed_status:
            return Response(
                {"error": f"Invalid status. Must be one of: {allowed_status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            enquiry = Enquiry.objects.select_related(
                "user",
                "hostel",
                "hostel__owner"
            ).get(
                id=enquiry_id,
                hostel__owner=request.user
            )
        except Enquiry.DoesNotExist:
            return Response(
                {"error": "Enquiry not found or unauthorized."},
                status=status.HTTP_404_NOT_FOUND
            )

        if status_value == "rejected":
            if not reason or len(reason.strip()) < 5:
                return Response(
                    {
                        "error": "A valid rejection reason with minimum 5 characters is required."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            enquiry.rejection_reason = reason.strip()

        else:
            enquiry.rejection_reason = None

        enquiry.status = status_value
        enquiry.save()

        # Live notification message
        notification_message = f"Your enquiry for {enquiry.hostel.name} was updated to {status_value}."

        if status_value == "accepted by owner":
            notification_message = f"Good news! Your enquiry for {enquiry.hostel.name} was accepted by the owner."

        elif status_value == "rejected":
            notification_message = f"Your enquiry for {enquiry.hostel.name} was rejected. Reason: {enquiry.rejection_reason}"

        elif status_value == "closed":
            notification_message = f"Your enquiry for {enquiry.hostel.name} was closed."

        send_client_notification(
            user_id=enquiry.user.id,
            message=notification_message,
            notification_type="enquiry_status_changed",
            data={
                "enquiry_id": enquiry.id,
                "hostel_id": enquiry.hostel.id,
                "hostel_name": enquiry.hostel.name,
                "status": enquiry.status,
                "rejection_reason": enquiry.rejection_reason,
            }
        )

        return Response(
            {
                "message": f"Enquiry marked as {status_value}",
                "enquiry_id": enquiry.id,
                "status": enquiry.status,
                "rejection_reason": enquiry.rejection_reason,
            },
            status=status.HTTP_200_OK
        )


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
    

class SubscriptionAmountView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):

        serializer = SubscriptionAmountSerializer(
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Subscription amount created",
                    "data": serializer.data
                },
                status=201
            )
        return Response(serializer.errors, status=400)
    def get(self, request):
        amounts = Subscription_Amount.objects.all().order_by("-created_at")
        serializer = SubscriptionAmountSerializer(
            amounts,
            many=True
        )
        return Response(serializer.data, status=200)
    


class CreateSubscriptionOrderView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        plan = request.data.get("plan")
        try:
            subscription_amount = Subscription_Amount.objects.get(
                plan=plan
            )
        except Subscription_Amount.DoesNotExist:
            return Response(
                {"error": "Subscription plan not found"},
                status=404
            )

        amount_in_paise = int(subscription_amount.amount * 100)

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        order = client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "payment_capture": 1,
            "notes": {
                "owner_id": request.user.id,
                "plan": plan,
            }
        })

        return Response({
            "order_id": order["id"],
            "amount": order["amount"],
            "currency": order["currency"],
            "key": settings.RAZORPAY_KEY_ID,
            "plan": plan,
        }, status=201)


class VerifySubscriptionPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")
        plan = request.data.get("plan")

        client = razorpay.Client(
            auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            )
        )

        try:

            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            })

        except Exception:

            return Response(
                {"error": "Payment verification failed"},
                status=400
            )

        subscription, created = OwnerSubscription.objects.get_or_create(
            owner=request.user
        )

        subscription.plan = plan

        if plan == "FREE":
            subscription.hostel_limit = 1

        elif plan == "PRO":
            subscription.hostel_limit = 5

        elif plan == "PREMIUM":
            subscription.hostel_limit = 20

        subscription.is_active = True
        subscription.save()

        return Response({
            "message": "Payment verified successfully",
            "plan": subscription.plan,
            "hostel_limit": subscription.hostel_limit,
            "is_active": subscription.is_active,
        }, status=200)
    

class SubscriptionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription, created = OwnerSubscription.objects.get_or_create(
            owner=request.user,
            defaults={
                "plan": "FREE",
                "hostel_limit": 1,
            }
        )
        return Response({
            "plan": subscription.plan,
            "hostel_limit": subscription.hostel_limit,
            "is_active": subscription.is_active,
        }, status=200)