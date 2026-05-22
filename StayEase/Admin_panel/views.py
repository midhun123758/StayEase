from Base_Panel.models import HostelDocument

from rest_framework.views import APIView

from App.models import User

from .serialzers import HostelDocumentSerializer

from rest_framework.response import Response

from rest_framework import status

from django.conf import settings

import boto3



class PendingDocumentsView(APIView):

    def get(self, request):

        documents = HostelDocument.objects.select_related(

            "uploaded_by",

            "hostel"

        ).all()


        serializer = HostelDocumentSerializer(

            documents,

            many=True

        )


        s3 = boto3.client(

            "s3",

            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,

            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,

            region_name="ap-south-1"

        )


        data = serializer.data


        for item in data:
            file_url = item.get("file_url")


            if file_url:

                try:
                    # Extract S3 object key
                    file_key = file_url.split(".com/")[-1]


                    signed_url = s3.generate_presigned_url(

                        "get_object",

                        Params={

                            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,

                            "Key": file_key

                        },
                        ExpiresIn=3600

                    )
                    item["pdf_url"] = signed_url
                except Exception as e:

                    item["pdf_url"] = None

                    item["pdf_error"] = str(e)


        return Response(data)



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
            else:

                return Response(

                    {
                        "error": "Invalid action"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            owner.save()


            return Response(

                {

                    "success": True,

                    "kyc_completed": owner.kyc_completed

                }

            )


        except User.DoesNotExist:

            return Response(

                {
                    "error": "Owner not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )