from django.urls import path 
from .views import AddHostlerView, AddRoomView, EnquiryListView, GenerateUploadURL, HostelListView,AddDocument, Room_listView,my_hostlers,OwnerChatListView
urlpatterns = [
    path('add_hostel/', HostelListView.as_view(), name='add_hostel'),
    path("generate-upload-url/", GenerateUploadURL.as_view()),
    path("add-document/", AddDocument.as_view()),
    path("my-hostlers/", my_hostlers.as_view()),
    path('add_hostler/', AddHostlerView.as_view(), name='add_hostler'),
    path("add-room/", AddRoomView.as_view(), name="add_room"),
    path("room-list/", Room_listView.as_view(), name="room_list"),
    path("enquiry-list/", EnquiryListView.as_view(), name="enquiry_list"),
    path("chatrooms/", OwnerChatListView.as_view(), name="owner_chatrooms")
]