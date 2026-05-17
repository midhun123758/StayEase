from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Base_Panel.models import AssignedMeal, Hostler, MessCharge
from App.models import KycDocument
from Base_Panel.serilalizers import AssignedMealSerializer
from .serializers import HostelViewSerializer,HostlerViewSerializer, PaymentSerializer,Room_Serializer,HostlerRoomSerializer
from Base_Panel.models import Transaction
from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import razorpay
from .models import MealResponse, RoomChatGroup, RoomChatMessage
from .serializers import RoomChatMessageSerializer


class Hostler_view(APIView):
    def get(sself,request):
        user=request.user
        try:
            hostler=Hostler.objects.get(user=user)
            serializer=HostlerViewSerializer(hostler)
            return Response(serializer.data, status=status.HTTP_200_OK )
        except Hostler.DoesNotExist:
            return Response({"error":"You are not assignd as a Hostler"},status=status.HTTP_404_NOT_FOUND)


class ViewMyHostel(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        try:
            hostler = Hostler.objects.get(user=user)

            if not hostler.hostel:
                return Response(
                    {"error": "No hostel assigned"},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = HostelViewSerializer(hostler.hostel)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Hostler.DoesNotExist:
            return Response(
                {"error": "Hostler not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
class PaymentsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            hostler = Hostler.objects.get(user=request.user)

            payments = Transaction.objects.filter(
                hostler=hostler
            ).order_by("-created_at")

            serializer = PaymentSerializer(
                payments,
                many=True
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except Hostler.DoesNotExist:

            return Response(
                {"error": "You are not assigned as a Hostler"},
                status=status.HTTP_404_NOT_FOUND
            )

client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)
class CreatePayment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            transaction = Transaction.objects.get(
                id=request.data["transaction_id"],
                hostler__user=request.user,
                status="pending"
            )

            amount = int(
                float(transaction.amount) * 100
            )

            order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": 1
            })

            transaction.razorpay_order_id = (
                order["id"]
            )

            transaction.save()

            return Response({
                "success": True,
                "order_id": order["id"],
                "amount": amount,
                "transaction_id": transaction.id,
                "key": settings.RAZORPAY_KEY_ID
            }, status=201)

        except Transaction.DoesNotExist:

            return Response({
                "success": False,
                "message": "Pending transaction not found"
            }, status=404)

        except Exception as e:

            return Response({
                "success": False,
                "message": str(e)
            }, status=500)
class VerifyPayment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:

            data = request.data

            transaction = Transaction.objects.get(
                razorpay_order_id=
                data["razorpay_order_id"],
                hostler__user=request.user
            )

            if transaction.status == "paid":

                return Response({
                    "success": False,
                    "message":
                    "Payment already verified"
                }, status=400)

            client.utility.verify_payment_signature({
                "razorpay_order_id":
                data["razorpay_order_id"],

                "razorpay_payment_id":
                data["razorpay_payment_id"],

                "razorpay_signature":
                data["razorpay_signature"],
            })

            transaction.status = "paid"

            transaction.payment_date = (
                timezone.now()
            )

            transaction.razorpay_payment_id = (
                data["razorpay_payment_id"]
            )

            transaction.razorpay_signature = (
                data["razorpay_signature"]
            )

            transaction.due_date = (
                timezone.now().date()
                + relativedelta(months=1)
            )

            transaction.save()

            return Response({
                "success": True,
                "message":
                "Payment Successful"
            })

        except Transaction.DoesNotExist:

            return Response({
                "success": False,
                "message":
                "Transaction not found"
            }, status=404)

        except Exception as e:

            return Response({
                "success": False,
                "message": str(e)
            }, status=400)
        
class my_room(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user 
        try:
           hostler = Hostler.objects.select_related("room").get(user=user)
           if  not hostler.room:
               return Response("room not asssignd yet",status=status.HTTP_404_NOT_FOUND)
           serializer = HostlerRoomSerializer(hostler)
           return Response(serializer.data, status=status.HTTP_200_OK)
        except Hostler.DoesNotExist:
            return Response(
                {"error": "You are not assigned as a hostler"},
                status=status.HTTP_404_NOT_FOUND
            )
           


class GPayPaymentView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id):

        try:

            transaction = Transaction.objects.get(
                id=transaction_id,
                hostler__user=request.user
            )

            owner = transaction.owner

            kyc = KycDocument.objects.get(
                user=owner
            )

            return Response({

                "success": True,

                "upi_id": kyc.upi_id,

                "account_holder_name":
                kyc.account_holder_name,

                "amount":
                transaction.amount,

                "transaction_id":
                transaction.id,

                "owner_name":
                owner.username

            }, status=status.HTTP_200_OK)

        except Transaction.DoesNotExist:

            return Response({

                "success": False,

                "message":
                "Transaction not found"

            }, status=status.HTTP_404_NOT_FOUND)

        except KycDocument.DoesNotExist:

            return Response({

                "success": False,

                "message":
                "Owner KYC not found"

            }, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:

            return Response({

                "success": False,

                "message": str(e)

            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RoomChatMessagesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):

        try:

            # Get logged-in hostler
            hostler = Hostler.objects.get(
                user=request.user
            )

            # Check if group exists
            group = RoomChatGroup.objects.get(
                id=group_id
            )

            # Security check
            if not group.members.filter(
                id=hostler.id
            ).exists():

                return Response(
                    {
                        "error": "You are not part of this room"
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get latest messages
            messages = group.messages.select_related(
                "sender"
            ).order_by("-created_at")[:50]

            # Reverse for oldest -> newest
            messages = reversed(messages)

            serializer = RoomChatMessageSerializer(
                messages,
                many=True
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        except Hostler.DoesNotExist:

            return Response(
                {
                    "error": "Hostler profile not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except RoomChatGroup.DoesNotExist:

            return Response(
                {
                    "error": "Room group not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
class MyRoomChatView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:

            hostler = Hostler.objects.get(
                user=request.user
            )

            if not hostler.room:

                return Response(
                    {
                        "error": "Room not assigned"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            group = RoomChatGroup.objects.get(
                room=hostler.room
            )

            return Response(
                {
                    "group_id": group.id,
                    "room_number": hostler.room.room_number
                },
                status=status.HTTP_200_OK
            )

        except Hostler.DoesNotExist:

            return Response(
                {
                    "error": "Hostler not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except RoomChatGroup.DoesNotExist:
            return Response(
                {
                    "error": "Room chat group not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        

class RespondMealView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        meal_id = request.data.get("meal_id")
        response_value = request.data.get("response")

        try:

            hostler = Hostler.objects.get(
                user=request.user
            )

            meal = AssignedMeal.objects.get(
                id=meal_id
            )

            # CHECK LOCK
            if meal.is_locked:
                return Response(
                    {"error": "Meal response locked"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # CHECK DEADLINE
            if meal.response_deadline and timezone.now() > meal.response_deadline:

                meal.is_locked = True
                meal.save()

                return Response(
                    {"error": "Response time expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            meal_response, created = MealResponse.objects.update_or_create(
                assigned_meal=meal,
                hostler=hostler,
                defaults={
                    "response": response_value
                }
            )

            # WANT → CREATE CHARGE
            if response_value == "WANT":

                MessCharge.objects.get_or_create(
                    hostel=meal.hostel,
                    hostler=hostler,
                    assigned_meal=meal,
                    date=meal.date,
                    meal_type=meal.meal_type,
                    defaults={
                        "amount": meal.amount_per_hostler
                    }
                )

            # DON'T WANT → REMOVE CHARGE
            else:

                MessCharge.objects.filter(
                    hostler=hostler,
                    assigned_meal=meal
                ).delete()

            return Response(
                {
                    "message": "Meal response updated",
                    "response": response_value,
                    "is_locked": meal.is_locked,
                    "response_deadline": meal.response_deadline,
                },
                status=status.HTTP_200_OK
            )

        except Hostler.DoesNotExist:

            return Response(
                {"error": "Hostler not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except AssignedMeal.DoesNotExist:

            return Response(
                {"error": "Meal not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:

            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        

class ReactMealView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        meal_id = request.data.get("meal_id")
        reaction = request.data.get("reaction")

        try:

            meal = AssignedMeal.objects.get(
                id=meal_id
            )

            # CHECK LOCK
            if meal.is_locked:
                return Response(
                    {"error": "Meal response locked"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # CHECK DEADLINE
            if meal.response_deadline and timezone.now() > meal.response_deadline:

                meal.is_locked = True
                meal.save()

                return Response(
                    {"error": "Response time expired"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = request.user

            # LIKE
            if reaction == "LIKE":

                meal.likes.add(user)
                meal.dislikes.remove(user)

            # DISLIKE
            elif reaction == "DISLIKE":

                meal.dislikes.add(user)
                meal.likes.remove(user)

            else:

                return Response(
                    {"error": "Invalid reaction"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {
                    "message": f"{reaction} added",
                    "total_likes": meal.likes.count(),
                    "total_dislikes": meal.dislikes.count(),
                    "is_locked": meal.is_locked,
                    "response_deadline": meal.response_deadline,
                },
                status=status.HTTP_200_OK
            )

        except AssignedMeal.DoesNotExist:

            return Response(
                {"error": "Meal not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:

            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class TodayMealsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:

            hostler = Hostler.objects.get(
                user=request.user
            )

            meals = AssignedMeal.objects.filter(
                hostel=hostler.hostel
            ).select_related(
                "meal_item"
            ).prefetch_related(
                "likes",
                "dislikes"
            ).order_by("-created_at")

            data = []

            for meal in meals:

                user_reaction = None

                if meal.likes.filter(
                    id=request.user.id
                ).exists():

                    user_reaction = "LIKE"

                elif meal.dislikes.filter(
                    id=request.user.id
                ).exists():

                    user_reaction = "DISLIKE"

                try:

                    meal_response = MealResponse.objects.get(
                        assigned_meal=meal,
                        hostler=hostler
                    )

                    user_response = meal_response.response

                except MealResponse.DoesNotExist:

                    user_response = None

                data.append({

                    "id":
                        meal.id,

                    "meal_name":
                        meal.meal_item.name
                        if meal.meal_item else None,

                    "meal_type":
                        meal.meal_type,

                    "description":
                        meal.description,

                    "meal_image":
                        request.build_absolute_uri(
                            meal.meal_image.url
                        )
                        if meal.meal_image else None,

                    "amount_per_hostler":
                        meal.amount_per_hostler,

                    "date":
                        meal.date,

                    "response_deadline":
                        meal.response_deadline,

                    "is_locked":
                        meal.is_locked,

                    "total_likes":
                        meal.likes.count(),

                    "total_dislikes":
                        meal.dislikes.count(),

                    "user_reaction":
                        user_reaction,

                    "user_response":
                        user_response,
                })

            return Response(
                data,
                status=status.HTTP_200_OK
            )

        except Hostler.DoesNotExist:

            return Response(
                {
                    "error": "Hostler not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )