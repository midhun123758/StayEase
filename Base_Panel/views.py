from django.shortcuts import render

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