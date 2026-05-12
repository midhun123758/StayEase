from django.urls import path 
from .views import AddHostlerView, AddRoomView, DailyMealAssignmentView, Enquery_change_view, EnquiryListView,Edit_hostel, FinancialOverviewView, GenerateUploadURL, HostelListView,AddDocument, Room_listView, RoomImagesListView,my_hostlers,OwnerChatListView,Meal_assignmentView,Owner_Profile
urlpatterns = [
    path('add_hostel/', HostelListView.as_view(), name='add_hostel'),
    path("generate-upload-url/", GenerateUploadURL.as_view()),
    path("add-document/", AddDocument.as_view()),
    path("my-hostlers/", my_hostlers.as_view()),
    path('add_hostler/', AddHostlerView.as_view(), name='add_hostler'),
    path("add-room/", AddRoomView.as_view(), name="add_room"),
    path("room-list/", Room_listView.as_view(), name="room_list"),
    path("enquiry-list/", EnquiryListView.as_view(), name="enquiry_list"),
    path("chatrooms/", OwnerChatListView.as_view(), name="owner_chatrooms"),

    path("meal-templates/", Meal_assignmentView.as_view(), name="meal_templates"),
    path("daily-assignments/", DailyMealAssignmentView.as_view(), name="daily_assignments"),
    path("enquery_edit/<int:enquiry_id>/",Enquery_change_view.as_view(),name="enquery_edit" ),
    path("financial-overview/", FinancialOverviewView.as_view(), name="financial_overview"),
    path("image_view/", RoomImagesListView.as_view(), name="image_view"),
    path("edit_hostel/", Edit_hostel.as_view(), name="edit_hostel"),
    path("owner_profile/", Owner_Profile.as_view(), name="owner_profile")

]