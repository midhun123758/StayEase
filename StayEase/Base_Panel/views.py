from django.shortcuts import render
from .models import AssignedMeal, ChatRoom, Hostel, HostelDocument, Hostler, MealTemplate, Room_image
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response            
from .serilalizers import AssignedMealSerializer, EnquirySerializer, HostelSerializer, HostlerCreateSerializer, HostlerSerializer
from rest_framework.permissions import IsAuthenticated
from .utils.s3 import generate_presigned_url
from .models import Room
from .serilalizers import RoomSerializer ,MealTemplateSerializer  
from Client_panel.models import Enquiry

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
        room_id = request.data.get("room")
        try:
            room = Room.objects.get(id=room_id)

        except Room.DoesNotExist:
            return Response(
                {"error": "Room not found"},
                status=404
            )

        # Count current hostlers in room
        current_hostlers = Hostler.objects.filter(
            room=room
        ).count()

        # Check bed space
        if current_hostlers >= room.bed_space:
            return Response(
                {"error": "This room is already full."},
                status=400
            )

        serializer = HostlerCreateSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():

            user = serializer.save()

            hostler = Hostler.objects.get(user=user)

            response_serializer = HostlerSerializer(hostler)

            return Response(
                response_serializer.data,
                status=201
            )

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

class Room_listView(APIView):
    def get(self, request):
        rooms= Room.objects.filter(hostel__owner=request.user)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)
    

class EnquiryListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        enqueries = Enquiry.objects.filter(hostel__owner=request.user)
        serializer = EnquirySerializer(enqueries, many=True)
        return Response(serializer.data)
# views.py
class OwnerChatListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filter ChatRooms where the logged-in user is the owner
        rooms = ChatRoom.objects.filter(owner=request.user).select_related('client', 'hostel')
        
        data = [{
            "id": r.id,
            "client": r.client.id, # Key: 'client' matches the query_param logic
            "client_username": r.client.username,
            "hostel": r.hostel.id, # Key: 'hostel' matches the URL logic
            "hostel_name": r.hostel.name,
            "last_message_preview": r.messages.last().message if r.messages.exists() else ""
        } for r in rooms]
        
        return Response(data)
    
class Meal_assignmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        hostel_id = request.data.get("hostel")
        try:
            # Verify ownership before allowing a new template to be added
            hostel = Hostel.objects.get(id=hostel_id, owner=request.user)
        except Hostel.DoesNotExist:
            return Response({"error": "Hostel not found or unauthorized"}, status=404)
        
        serializer = MealTemplateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(hostel=hostel)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        # FIXED: Retrieve ID from URL parameters (?hostel=2)
        hostel_id = request.query_params.get("hostel")
        
        if not hostel_id:
            return Response({"error": "Hostel ID is required"}, status=400)

        try:
            hostel = Hostel.objects.get(id=hostel_id, owner=request.user)
        except Hostel.DoesNotExist:
            return Response({"error": "Hostel not found or unauthorized"}, status=404)   
        
        # Only return meals that have not been soft-deleted
        meals = MealTemplate.objects.filter(hostel=hostel, is_deleted=False)
        serializer = MealTemplateSerializer(meals, many=True)
        return Response(serializer.data, status=200)

    def delete(self, request):
        meal_id = request.data.get("meal_id")
        try:
            # Ensure the meal belongs to a hostel owned by the user
            meal = MealTemplate.objects.get(id=meal_id, hostel__owner=request.user)
            meal.is_deleted = True
            meal.save()
            return Response({"message": "Meal template deleted"}, status=200)
        except MealTemplate.DoesNotExist:
            return Response({"error": "Meal template not found"}, status=404)
        
class DailyMealAssignmentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        hostel_id = request.data.get("hostel")
        meal_item_id = request.data.get("meal_item")
        date = request.data.get("date")
        meal_type = request.data.get("meal_type")

        try:
            # 1. Verify hostel ownership
            hostel = Hostel.objects.get(id=hostel_id, owner=request.user)
            
            # 2. Verify the meal item exists in this hostel's library
            meal_item = MealTemplate.objects.get(id=meal_item_id, hostel=hostel)
            
            # 3. Update if a meal is already assigned to that slot, else create
            assignment, created = AssignedMeal.objects.update_or_create(
                hostel=hostel,
                date=date,
                meal_type=meal_type,
                defaults={'meal_item': meal_item}
            )
            
            serializer = AssignedMealSerializer(assignment)
            status_code = 201 if created else 200
            return Response(serializer.data, status=status_code)
            
        except Hostel.DoesNotExist:
            return Response({"error": "Hostel not found or unauthorized"}, status=404)
        except MealTemplate.DoesNotExist:
            return Response({"error": "Meal item not found in your library"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def get(self, request):
        hostel_id = request.query_params.get("hostel")
        date = request.query_params.get("date") 

        if not hostel_id or not date:
            return Response({"error": "hostel and date parameters are required"}, status=400)

        assignments = AssignedMeal.objects.filter(hostel_id=hostel_id, date=date)
        serializer = AssignedMealSerializer(assignments, many=True)
        return Response(serializer.data, status=200)