from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Base_Panel.models import Hostler
from .serializers import HostelViewSerializer,HostlerViewSerializer,Room_Serializer,HostlerRoomSerializer
from Base_Panel.models import Transaction
from .serializers import payment_serilizer
from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.utils import timezone
import razorpay

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
        
class payments_view(APIView):
    def get(self,request):
        user=request.user
        hostler=Hostler.objects.get(user=user)
        try:
            payments=Transaction.objects.filter(hostler=hostler).order_by("-created_at")
            serializer=payment_serilizer(payments,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK )
        except Hostler.DoesNotExist:
            return Response({"error":"You are not assignd as a Hostler"})
            

client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)

class CreatePayment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        hostler = Hostler.objects.get(
            user=request.user
        )
        amount = int(
            hostler.monthly_rent * 100
        )

        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        transaction = Transaction.objects.create(
            hostler=hostler,
            owner=hostler.owner,
            amount=hostler.monthly_rent,
            razorpay_order_id=order["id"]
        )

        return Response({
            "success": True,
            "order_id": order["id"],
            "amount": amount,
            "key": settings.RAZORPAY_KEY_ID
        })
    

class VerifyPayment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        data = request.data

        transaction = Transaction.objects.get(
            razorpay_order_id=
            data["razorpay_order_id"]
        )

        params_dict = {

            "razorpay_order_id":
            data["razorpay_order_id"],

            "razorpay_payment_id":
            data["razorpay_payment_id"],

            "razorpay_signature":
            data["razorpay_signature"],
        }

        client.utility.verify_payment_signature(
            params_dict
        )

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
           


