from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Base_Panel.models import Hostler
from .serializers import HostelViewSerializer,HostlerViewSerializer

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
        
