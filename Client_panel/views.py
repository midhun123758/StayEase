import math
from rest_framework.views import APIView
from rest_framework.response import Response
from Base_Panel.models import Hostel
from .serializers import HostelSerializer
from .models import Enquiry
from rest_framework.permissions import IsAuthenticated

class SearchHostelView(APIView):
    def post(self, request):
        user_lat = float(request.data.get("latitude"))
        user_lng = float(request.data.get("longitude"))

        radius_km = 20  # 🔥 change this (10km, 20km, etc.)

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
    permission_classes = [IsAuthenticated]

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
            stay_days=request.data.get("stay_days"),
            message=request.data.get("message"),
        )

        return Response({"message": "Enquiry sent successfully"}, status=201)