from django.urls import path,include
from .views import SearchHostelView,HostelDetailView
urlpatterns = [
    path('search/',SearchHostelView.as_view(), name='search-hostels'),
    path('hostel/<int:hostel_id>/', HostelDetailView.as_view(), name='hostel-detail'),
]
