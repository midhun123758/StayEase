from django.urls import path 
from .views import AddHostlerView, AddRoomView, GenerateUploadURL, HostelListView,AddDocument,my_hostlers
urlpatterns = [
    path('add_hostel/', HostelListView.as_view(), name='add_hostel'),
    path("generate-upload-url/", GenerateUploadURL.as_view()),
    path("add-document/", AddDocument.as_view()),
    path("my-hostlers/", my_hostlers.as_view()),
    path('add_hostler/', AddHostlerView.as_view(), name='add_hostler'),
    path("add-room/", AddRoomView.as_view(), name="add_room"),
]