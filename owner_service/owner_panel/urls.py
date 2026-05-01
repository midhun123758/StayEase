from .views import HostelListView
from django.urls import path
urlpatterns = [
    path('hostels_adding/', HostelListView.as_view(), name='hostel-list'), 
]