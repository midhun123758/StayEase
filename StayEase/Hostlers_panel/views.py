from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Base_Panel.models import Hostler
from App.models import KycDocument
from .serializers import HostelViewSerializer,HostlerViewSerializer, PaymentSerializer,Room_Serializer,HostlerRoomSerializer
from Base_Panel.models import Transaction
from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import razorpay
from .models import RoomChatGroup, RoomChatMessage
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

        group = RoomChatGroup.objects.get(id=group_id)

        messages = group.messages.select_related(
            "sender"
        ).order_by("created_at")

        serializer = RoomChatMessageSerializer(
            messages,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request, group_id):

        group = RoomChatGroup.objects.get(id=group_id)

        hostler = Hostler.objects.get(
            user=request.user
        )

        if hostler not in group.members.all():

            return Response({
                "error":
                "You are not part of this room"
            }, status=403)

        message = RoomChatMessage.objects.create(
            group=group,
            sender=request.user,
            message=request.data.get("message")
        )

        serializer = RoomChatMessageSerializer(message)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )