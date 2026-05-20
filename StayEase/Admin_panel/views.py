from Base_Panel.models import HostelDocument
from rest_framework.views import APIView
from App.models import User
from .serialzers import HostelDocumentSerializer
from rest_framework.response import Response
from rest_framework import status


class PendingDocumentsView(APIView):

    def get(self, request):

        documents = HostelDocument.objects.select_related(
            "uploaded_by",
            "hostel"
        )

        serializer = HostelDocumentSerializer(
            documents,
            many=True
        )

        return Response(serializer.data)


class VerifyOwnerKYC(APIView):

    def post(self, request, user_id):

        action = request.data.get("action")

        try:

            owner = User.objects.get(
                id=user_id,
                role="owner"
            )

            if action == "approve":
                owner.kyc_completed = True

            elif action == "reject":
                owner.kyc_completed = False

            owner.save()

            return Response({
                "success": True,
                "kyc_completed": owner.kyc_completed
            })

        except User.DoesNotExist:

            return Response({
                "error": "Owner not found"
            }, status=status.HTTP_404_NOT_FOUND)