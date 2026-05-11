import math
from rest_framework.views import APIView
from rest_framework.response import Response
from Base_Panel.models import Hostel
from .serializers import EnquirySerializer, HostelSerializer
from .models import Enquiry
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from .models import HostelMessage
from App.models import User
from rest_framework.permissions import IsAuthenticated
from Base_Panel.models import ChatRoom
from rest_framework import status
from django.shortcuts import get_object_or_404
class SearchHostelView(APIView):

    permission_classes = [AllowAny]
    def post(self, request):
        user_lat = float(request.data.get("latitude"))
        user_lng = float(request.data.get("longitude"))

        radius_km = 20  

        nearby_hostels = []

        for hostel in Hostel.objects.all():
            distance = self.haversine(
                user_lat, user_lng,
                hostel.latitude, hostel.longitude
            )

            if distance <= radius_km:
                nearby_hostels.append(hostel)
        serializer = HostelSerializer(nearby_hostels, many=True)
        return Response(serializer.data)

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in KM
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        return R * c
    

class HostelDetailView(APIView):
    def get(self,request,hostel_id):
        try:
            hostel=Hostel.objects.get(id=hostel_id)
            serilaizer=HostelSerializer(hostel)
            return Response(serilaizer.data)
        except Hostel.DoesNotExist:
            return Response({"error":"Hostel not found"},status=404)
        except Exception as e:
            return Response({"error":str(e)},status=500)        
        

class CreateEnquiryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, hostel_id):
        try:
            hostel = Hostel.objects.get(id=hostel_id)
        except Hostel.DoesNotExist:
            return Response({"error": "Hostel not found"}, status=404)

        enquiry = Enquiry.objects.create(
            user=request.user,
            hostel=hostel,
            full_name=request.data.get("full_name"),
            email=request.data.get("email"),
            phone=request.data.get("phone"),
            preferred_date=request.data.get("preferred_date"),
            stay_months=request.data.get("stay_months"),
            message=request.data.get("message"),
        )

        return Response({"message": "Enquiry sent successfully"}, status=201)
    



class UserDetailView(APIView):
    """
    REQUIRED: Fixes the 404 [object Object] error by providing 
    the host's info to the chat header.
    """
    def get(self, request, user_id):
        user_obj = get_object_or_404(User, id=user_id)
        return Response({
            "id": user_obj.id,
            "username": user_obj.username,
            "email": user_obj.email
        })


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hostel_id):
        # The Owner sends this as ?client_id=X
        client_id = request.query_params.get('client_id')

        if client_id:
            # CASE: Owner is viewing history
            # We filter by the client_id passed from the sidebar
            messages = HostelMessage.objects.filter(
                chatroom__hostel_id=hostel_id,
                chatroom__client_id=client_id,
                chatroom__owner=request.user
            ).order_by('created_at')
        else:
            # CASE: Client is viewing history
            messages = HostelMessage.objects.filter(
                chatroom__hostel_id=hostel_id,
                chatroom__client=request.user
            ).order_by('created_at')

        data = [
            {
                "id": m.id,
                "message": m.message,
                "sender": m.sender.username,
                "sender_id": m.sender.id,
                "created_at": m.created_at,
            }
            for m in messages
        ]
        return Response(data)

# class All_hostels(APIView):
#     def get(self,request):
#         hostels=Hostel.objects.all()
#         serializer=HostelSerializer(hostels,many=True)
#         return Response(serializer.data)
class ClientEnquiryListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns a list of enquiries made by the currently logged-in user.
        Includes the rejection_reason and status_display.
        """
        enquiries = Enquiry.objects.filter(user=request.user).order_by('-created_at')
        serializer = EnquirySerializer(enquiries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
