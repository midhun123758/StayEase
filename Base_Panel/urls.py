from django.urls import path 
from .views import HostelListView
urlpatterns = [
    path('add_hostel/', HostelListView.as_view(), name='add_hostel'),
]