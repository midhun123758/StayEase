from django.urls import path,include
from .views import SearchHostelView
urlpatterns = [
    path('search/',SearchHostelView.as_view(), name='search-hostels'),
]
