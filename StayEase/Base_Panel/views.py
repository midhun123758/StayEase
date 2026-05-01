from django.shortcuts import render
from .models import Hostel
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response            
from .serilalizers import HostelSerializer
from rest_framework.permissions import IsAuthenticated
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
        serializer = HostelerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)