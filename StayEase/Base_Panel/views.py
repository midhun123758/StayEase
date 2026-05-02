from django.shortcuts import render
from .models import Hostel, HostelDocument
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response            
from .serilalizers import HostelSerializer, HostlerCreateSerializer
from rest_framework.permissions import IsAuthenticated
from .utils.s3 import generate_presigned_url


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


class Add_HostlerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = HostlerCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
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