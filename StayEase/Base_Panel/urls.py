from django.urls import path 
from .views import GenerateUploadURL, HostelListView,AddDocument
urlpatterns = [
    path('add_hostel/', HostelListView.as_view(), name='add_hostel'),
    path("generate-upload-url/", GenerateUploadURL.as_view()),
    path("add-document/", AddDocument.as_view())
]