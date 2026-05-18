# # from django.shortcuts import render
# # from django.utils import timezone
# # # Create your views here.
# # # Admin_panel/views.py

# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework import status

# # from .permissions import IsPlatformAdmin
# # # from .models import OwnerVerification
# # # from .serializers import OwnerVerificationSerializer
# # import boto3

# # from django.conf import settings

# # # class PendingOwnersView(APIView):

# # #     permission_classes = [IsPlatformAdmin]

# # #     def get(self, request):

# # #         owners = OwnerVerification.objects.filter(
# # #             status="PENDING"
# # #         )

# # #         serializer = OwnerVerificationSerializer(
# # #             owners,
# # #             many=True
# # #         )

# # #         return Response(
# # #             serializer.data,
# # #             status=status.HTTP_200_OK
# # #         )
    
# # # class ApproveOwnerView(APIView):

# # #     permission_classes = [IsPlatformAdmin]

# # #     def post(self, request, verification_id):

# # #         verification = OwnerVerification.objects.get(
# # #             id=verification_id
# # #         )

# # #         verification.status = "APPROVED"

# # #         verification.verified_by = request.user

# # #         verification.verified_at = timezone.now()

# # #         verification.save()

# # #         verification.owner.kyc_completed = True
# # #         verification.owner.save()

# # #         return Response({
# # #             "message": "Owner approved successfully"
# # #         })
    

# # class ViewImage(APIView):

# #     def get(self, request):

# #         file_key = "documents/test.jpg"

# #         s3 = boto3.client(
# #             "s3",
# #             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
# #             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
# #             region_name=settings.AWS_S3_REGION_NAME
# #         )

# #         image_url = s3.generate_presigned_url(
# #             ClientMethod="get_object",

# #             Params={
# #                 "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
# #                 "Key": file_key
# #             },

# #             ExpiresIn=3600
# #         )

# #         return Response({
# #             "image_url": image_url
# #         })

# # Admin_panel/views.py
# # Admin_panel/views.py
# import os
# import boto3

# from botocore.client import Config

# from dotenv import load_dotenv

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status


# load_dotenv()


# class ViewAllImages(APIView):

#     def get(self, request):

#         try:

#             s3 = boto3.client(

#                 "s3",

#                 aws_access_key_id=os.getenv(
#                     "AWS_ACCESS_KEY_ID"
#                 ),

#                 aws_secret_access_key=os.getenv(
#                     "AWS_SECRET_ACCESS_KEY"
#                 ),

#                 region_name=os.getenv(
#                     "AWS_REGION"
#                 ),

#                 config=Config(
#                     signature_version="s3v4"
#                 )
#             )

#             response = s3.list_objects_v2(

#                 Bucket=os.getenv(
#                     "AWS_STORAGE_BUCKET_NAME"
#                 )
#             )

#             files = response.get(
#                 "Contents",
#                 []
#             )

#             images = []

#             for file in files:

#                 file_key = file.get("Key")

#                 if not file_key:
#                     continue

#                 image_url = s3.generate_presigned_url(

#                     ClientMethod="get_object",

#                     Params={

#                         "Bucket": os.getenv(
#                             "AWS_STORAGE_BUCKET_NAME"
#                         ),

#                         "Key": file_key
#                     },

#                     ExpiresIn=3600
#                 )

#                 images.append({

#                     "file_key": file_key,

#                     "image_url": image_url
#                 })

#             return Response({

#                 "success": True,

#                 "images": images

#             }, status=status.HTTP_200_OK)

#         except Exception as e:

#             return Response({

#                 "success": False,

#                 "error": str(e)

#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)