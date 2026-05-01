from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Hostel
from .serializers import HostelSerializer
from .utils import get_user_id_from_token


class HostelListView(APIView):

    def get(self, request):
        hostels = Hostel.objects.all()
        serializer = HostelSerializer(hostels, many=True)
        return Response(serializer.data)

    def post(self, request):
        owner_user_id = get_user_id_from_token(request)

        if not owner_user_id:
            return Response({"error": "Invalid or missing token"}, status=401)

        serializer = HostelSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(owner_user_id=owner_user_id)
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)