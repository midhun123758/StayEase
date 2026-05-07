from django.shortcuts import render
from .models import Hostel, HostelDocument, Hostler, Room_image
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response            
from .serilalizers import HostelSerializer, HostlerCreateSerializer, HostlerSerializer
from rest_framework.permissions import IsAuthenticated
from .utils.s3 import generate_presigned_url
from .models import Room
from .serilalizers import RoomSerializer    

class HostelListView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = HostelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    def get(self, request):
        hostels = Hostel.objects.filter(owner=request.user)
        serializer = HostelSerializer(hostels, many=True)
        return Response(serializer.data)
    
class AddHostlerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = HostlerCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            user = serializer.save()

            hostler = Hostler.objects.get(user=user)

            response_serializer = HostlerSerializer(hostler)

            return Response(response_serializer.data, status=201)

        return Response(serializer.errors, status=400)

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
        hostlers = (
            Hostler.objects
            .filter(owner=request.user, is_active=True)
            .select_related("user", "hostel", "room")
        )

        serializer = HostlerSerializer(hostlers, many=True)
        return Response(serializer.data, status=200)
    
class AddRoomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        hostel_id = request.data.get("hostel_id")

        try:
            hostel = Hostel.objects.get(
                id=hostel_id,
                owner=request.user
            )

        except Hostel.DoesNotExist:
            return Response(
                {"error": "Hostel not found or unauthorized"},
                status=404
            )

        serializer = RoomSerializer(data=request.data)

        if serializer.is_valid():

      
            room = serializer.save(hostel=hostel)

         
            images = request.data.getlist("images")

        
            for image in images:
                Room_image.objects.create(
                    room=room,
                    image=image
                )

            return Response({
                "message": "Room created successfully",
                "room": serializer.data
            }, status=201)

        return Response(serializer.errors, status=400)