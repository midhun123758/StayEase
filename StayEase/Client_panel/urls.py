from django.urls import path,include
from .views import CreateEnquiryView, SearchHostelView,HostelDetailView,ChatHistoryView, UserDetailView,ClientEnquiryListView
urlpatterns = [
    path('search/',SearchHostelView.as_view(), name='search-hostels'),
    path('hostel/<int:hostel_id>/', HostelDetailView.as_view(), name='hostel-detail'),
    path('hostels/<int:hostel_id>/enquiry/', CreateEnquiryView.as_view()),
    path('hostel/<int:hostel_id>/history/', ChatHistoryView.as_view(), name='chat-history'),
    path('api/user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    # path('hostels/', All_hostels.as_view(), name='all-hostels'),
    path('enquiry_view/',ClientEnquiryListView.as_view(),name='enquiry_view' )
]
    