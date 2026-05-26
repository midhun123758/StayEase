
from django.utils import timezone
from django.shortcuts import render
from rest_framework import status
from App.models import User
from Hostlers_panel.models import MealResponse
from .models import AssignedMeal, BlacklistedHostler, ChatRoom, Hostel, HostelDocument, HostelFeedback, Hostler, MealTemplate, MessCharge, Room_image, Subscription_Amount, Transaction
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response            
from .serilalizers import AssignedMealSerializer, CollectPaymentSerializer, EnquirySerializer, HostelFeedbackSerializer, HostelSerializer, HostlerCheckoutSerializer, HostlerCreateSerializer, HostlerSerializer, RoomImageSerializer, SubscriptionAmountSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from .utils.s3 import generate_presigned_url
from .models import Room
from .serilalizers import RoomSerializer ,MealTemplateSerializer  
from Client_panel.models import Enquiry
from django.db import transaction
from django.db.models import Avg, Sum, Q
from rest_framework.parsers import MultiPartParser,FormParser
from .models import OwnerSubscription
import razorpay
from django.conf import settings
from Client_panel.utils import send_client_notification
from datetime import timedelta
from decimal import Decimal
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.mail import send_mail


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

        monthly_rent = request.data.get(
            "monthly_rent"
        )

        # VALIDATE RENT

        if not monthly_rent:

            return Response({
                "error":
                    "Monthly rent is required."
            }, status=400)

        try:

            monthly_rent = Decimal(
                str(monthly_rent)
            )

        except Exception:

            return Response({
                "error":
                    "Invalid monthly rent amount."
            }, status=400)

        # GET ROOM

        try:

            room = Room.objects.get(
                id=room_id
            )

        except Room.DoesNotExist:

            return Response({
                "error":
                    "Room not found"
            }, status=404)

        # CHECK ROOM CAPACITY

        current_hostlers = (
            Hostler.objects.filter(
                room=room
            ).count()
        )

        if current_hostlers >= room.bed_space:

            return Response({
                "error":
                    "This room is already full."
            }, status=400)

        try:

            with transaction.atomic():

                serializer = (
                    HostlerCreateSerializer(
                        data=request.data,
                        context={
                            "request": request
                        }
                    )
                )

                if serializer.is_valid():

                    # CREATE USER

                    user = serializer.save()

                    # GET HOSTLER

                    hostler = Hostler.objects.get(
                        user=user
                    )

                    # SAVE RENT

                    hostler.monthly_rent = (
                        monthly_rent
                    )

                    hostler.save()

                    # CREATE INITIAL TRANSACTION

                    Transaction.objects.create(

                        hostler=hostler,

                        owner=request.user,

                        amount=monthly_rent,

                        paid_amount=Decimal("0.00"),

                        remaining_amount=monthly_rent,

                        payment_type="rent",

                        status="pending",

                        billing_date=(
                            timezone.now().date()
                        )
                    )

                    response_serializer = (
                        HostlerSerializer(
                            hostler
                        )
                    )

                    return Response(
                        response_serializer.data,
                        status=201
                    )

                return Response(
                    serializer.errors,
                    status=400
                )

        except Exception as e:

            return Response({
                "error": str(e)
            }, status=500)
        

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
                    "response_deadline": timezone.now() + timedelta(minutes=3),
                    "is_locked":False,
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

            return Response({
                "error": "Hostel ID required"
            }, status=400)

        transactions = Transaction.objects.filter(
            hostler__owner=owner,
            hostler__hostel_id=hostel_id
        )

        stats = transactions.aggregate(

            total_pending=Sum(
                "amount",
                filter=Q(status="pending")
            ),

            total_collected=Sum(
                "amount",
                filter=Q(status="paid")
            ),
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
                    filter=Q(
                        transactions__status="pending"
                    )
                )

            )

            .select_related(
                "user",
                "room"
            )

            .distinct()
        )

        hostler_dues = [

            {

                "name":
                    h.user.username,

                "room":
                    h.room.room_number
                    if h.room else "N/A",

                "amount_due":
                    h.total_due or 0,

                "phone":
                    h.phone,

                "transactions": [

                    {
                        "transaction_id":
                            t.id,

                        "amount":
                            t.amount,

                        "payment_type":
                            t.payment_type,

                        "status":
                            t.status,
                    }

                    for t in Transaction.objects.filter(
                        hostler=h,
                        status="pending"
                    )
                ]
            }

            for h in pending_hostlers
        ]

        pending = (
            stats["total_pending"] or 0
        )

        collected = (
            stats["total_collected"] or 0
        )

        return Response({

            "summary": {

                "pending":
                    pending,

                "collected":
                    collected,

                "total_expected":
                    pending + collected,
            },

            "payable_list":
                hostler_dues,

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
    

class MealResponsesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, meal_id):
        try:

            meal = AssignedMeal.objects.get(
                id=meal_id,
                hostel__owner=request.user
            )

            responses = MealResponse.objects.filter(
                assigned_meal=meal
            ).select_related("hostler__user")

            response_data = []

            for response in responses:

                response_data.append({
                    "hostler_name":
                        response.hostler.user.username,

                    "response":
                        response.response
                })

            likes = meal.likes.values_list(
                "username",
                flat=True
            )
            dislikes = meal.dislikes.values_list(
                "username",
                flat=True
            )
            return Response(
                {
                    "meal": meal.meal_item.name
                        if meal.meal_item else None,

                    "responses": response_data,

                    "likes": list(likes),

                    "dislikes": list(dislikes),
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        

# Base_Panel/views.py

class HostelFeedbackCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, hostel_id):

        try:

            hostel = Hostel.objects.get(id=hostel_id)

        except Hostel.DoesNotExist:

            return Response({
                "error": "Hostel not found"
            }, status=404)

        if HostelFeedback.objects.filter(
            hostel=hostel,
            user=request.user
        ).exists():

            return Response({
                "error": "Feedback already submitted"
            }, status=400)

        serializer = HostelFeedbackSerializer(
            data=request.data
        )

        if serializer.is_valid():

            serializer.save(
                user=request.user,
                hostel=hostel
            )

            return Response(
                serializer.data,
                status=201
            )

        return Response(
            serializer.errors,
            status=400
        )
    

class OwnerReplyFeedbackView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, feedback_id):

        try:

            feedback = HostelFeedback.objects.get(
                id=feedback_id
            )

        except HostelFeedback.DoesNotExist:

            return Response({
                "error": "Feedback not found"
            }, status=404)

        if feedback.hostel.owner != request.user:

            return Response({
                "error": "Permission denied"
            }, status=403)

        feedback.owner_reply = request.data.get(
            "owner_reply"
        )

        feedback.save()

        return Response({
            "message": "Reply added"
        })


class HostelFeedbackListView(APIView):

    def get(self, request, hostel_id):

        feedbacks = HostelFeedback.objects.filter(
            hostel_id=hostel_id
        ).order_by("-created_at")

        serializer = HostelFeedbackSerializer(
            feedbacks,
            many=True
        )

        average_rating = feedbacks.aggregate(
            avg=Avg("rating")
        )["avg"]

        return Response({

            "average_rating": average_rating,

            "total_reviews": feedbacks.count(),

            "reviews": serializer.data

        })
class HostlerCheckoutView(APIView):

    authentication_classes = [JWTAuthentication]

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        owner = request.user

        # 1. PERMISSION CHECK

        if owner.role != "owner":

            return Response({

                "success": False,

                "message":
                    "Only owners can checkout hostlers"

            }, status=status.HTTP_403_FORBIDDEN)

        # 2. VALIDATE INPUT

        serializer = HostlerCheckoutSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response({

                "success": False,

                "message":
                    "Invalid input data",

                "errors":
                    serializer.errors

            }, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # 3. GET HOSTLER USER

        try:

            hostler_user = (
                User.objects
                .select_for_update()
                .get(

                    username=data["username"],

                    email=data["email"],

                    role="hostler",

                    owner=owner
                )
            )

        except User.DoesNotExist:

            return Response({

                "success": False,

                "message":
                    "Hostler not found under this owner"

            }, status=status.HTTP_404_NOT_FOUND)

        # 4. GET HOSTLER PROFILE

        try:

            hostler_profile = (
                Hostler.objects
                .select_for_update()
                .get(user=hostler_user)
            )

        except Hostler.DoesNotExist:

            hostler_profile = None

        # 5. CHECK PENDING PAYMENTS

        pending_transaction_amount = (
            Decimal("0.00")
        )

        unpaid_mess_amount = (
            Decimal("0.00")
        )

        if hostler_profile:

            pending_transaction_amount = (

                Transaction.objects.filter(

                    hostler=hostler_profile,

                    status__in=[
                        "pending",
                        "overdue",
                        "partial"
                    ]

                ).aggregate(

                    total=Sum(
                        "remaining_amount"
                    )

                )["total"]

                or Decimal("0.00")
            )

            unpaid_mess_amount = (

                MessCharge.objects.filter(

                    hostler=hostler_profile,

                    is_paid=False

                ).aggregate(

                    total=Sum("amount")

                )["total"]

                or Decimal("0.00")
            )

        total_pending_amount = (
            pending_transaction_amount +
            unpaid_mess_amount
        )

        # 6. BLOCK CHECKOUT IF PENDING

        if total_pending_amount > 0:

            return Response({

                "success": False,

                "message":
                    "Checkout blocked due to pending payments",

                "pending_amount":
                    float(total_pending_amount),

                "transaction_pending":
                    float(
                        pending_transaction_amount
                    ),

                "mess_pending":
                    float(
                        unpaid_mess_amount
                    )

            }, status=status.HTTP_400_BAD_REQUEST)

        # 7. ROOM RELEASE

        room = (
            hostler_profile.room
            if hostler_profile else None
        )

        if room:

            room.is_available = True

            room.save()

        # 8. BLACKLIST ENTRY

        BlacklistedHostler.objects.update_or_create(

            owner=owner,

            hostler=hostler_user,

            defaults={

                "room":
                    room,

                "reason":
                    data["reason"]
            }
        )

        # 9. UPDATE HOSTLER PROFILE

        if hostler_profile:

            hostler_profile.room = None

            hostler_profile.is_active = False

            hostler_profile.check_out_date = (
                timezone.now().date()
            )

            hostler_profile.save()

        # 10. UPDATE USER

        hostler_user.owner = None

        hostler_user.role = "user"

        hostler_user.save()

        # 11. SEND THANK YOU EMAIL

        try:

            send_mail(

                subject=(
                    "Thank You for Staying with StayEase"
                ),

                message=f"""
Hello {hostler_user.username},

Thank you for staying with us.

Your checkout has been completed successfully.

We truly appreciate your time at the hostel and hope you had a safe and comfortable stay.

If you have any questions or future accommodation needs, feel free to contact us again.

We wish you success and happiness ahead.

Warm regards,
StayEase Team
""",

                from_email=(
                    settings.EMAIL_HOST_USER
                ),

                recipient_list=[
                    hostler_user.email
                ],

                fail_silently=True,
            )

        except Exception as e:

            print("EMAIL ERROR:", e)

        # 12. SUCCESS RESPONSE

        return Response({

            "success": True,

            "message":
                "Hostler checked out successfully",

            "hostler": {

                "id":
                    hostler_user.id,

                "username":
                    hostler_user.username,

                "email":
                    hostler_user.email,

                "new_role":
                    hostler_user.role
            },

            "blacklisted":
                True

        }, status=status.HTTP_200_OK)
    
class CollectPaymentView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CollectPaymentSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response({

                "success": False,

                "errors":
                    serializer.errors

            }, status=400)

        data = serializer.validated_data

        # GET TRANSACTION

        try:

            transaction = Transaction.objects.get(

                id=data["transaction_id"],

                owner=request.user
            )

        except Transaction.DoesNotExist:

            return Response({

                "success": False,

                "message":
                    "Transaction not found"

            }, status=404)

        # SAFE DECIMAL

        amount = Decimal(
            str(data["amount"])
        )

        transaction_remaining = Decimal(
            str(transaction.remaining_amount)
        )

        # VALIDATION

        if amount <= 0:

            return Response({

                "success": False,

                "message":
                    "Invalid payment amount"

            }, status=400)

        # EXTRA PAYMENT
        # FOR MESS CHARGES

        extra_payment = (
            amount -
            transaction_remaining
        )

        # UPDATE TRANSACTION

        if amount >= transaction_remaining:

            transaction.paid_amount = (

                Decimal(
                    str(transaction.paid_amount)
                )

                +

                transaction_remaining
            )

            transaction.remaining_amount = (
                Decimal("0.00")
            )

            transaction.status = "paid"

        else:

            transaction.paid_amount = (

                Decimal(
                    str(transaction.paid_amount)
                )

                +

                amount
            )

            transaction.remaining_amount = (

                transaction_remaining -
                amount
            )

            transaction.status = "partial"

        # PAYMENT DETAILS

        transaction.payment_method = (
            data["payment_method"]
        )

        transaction.payment_note = (
            data.get("payment_note", "")
        )

        transaction.collected_by = (
            request.user
        )

        transaction.payment_date = (
            timezone.now()
        )

        transaction.save()

        # HANDLE MESS PAYMENT

        if extra_payment > 0:

            unpaid_mess_charges = (

                MessCharge.objects.filter(

                    hostler=transaction.hostler,

                    is_paid=False

                ).order_by("id")
            )

            for mess in unpaid_mess_charges:

                if extra_payment <= 0:
                    break

                mess_amount = Decimal(
                    str(mess.amount)
                )

                if extra_payment >= mess_amount:

                    mess.is_paid = True

                    mess.save()

                    extra_payment -= (
                        mess_amount
                    )

        # REMAINING MESS

        remaining_mess = (

            MessCharge.objects.filter(

                hostler=transaction.hostler,

                is_paid=False

            ).aggregate(

                total=Sum("amount")

            )["total"]

            or Decimal("0.00")
        )

        # RESPONSE

        return Response({

            "success": True,

            "message":
                "Payment collected successfully",

            "transaction": {

                "id":
                    transaction.id,

                "total_amount":
                    float(transaction.amount),

                "paid_amount":
                    float(transaction.paid_amount),

                "remaining_amount":
                    float(
                        transaction.remaining_amount
                    ),

                "status":
                    transaction.status,

                "payment_method":
                    transaction.payment_method
            },

            "remaining_mess_pending":
                float(remaining_mess)

        }, status=status.HTTP_200_OK)