from django.urls import path 
from .views import AddHostlerView, AddRoomView, DailyMealAssignmentView, Enquery_change_view, EnquiryListView, FinancialOverviewView, GenerateUploadURL, HostelListView,AddDocument, Room_listView, SavePanoramaView,my_hostlers,OwnerChatListView,Meal_assignmentView
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
    path('rooms/upload-image/', SavePanoramaView.as_view(), name='room-image-upload'),

]