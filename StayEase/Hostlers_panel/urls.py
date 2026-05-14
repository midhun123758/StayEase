

from .views import ViewMyHostel,Hostler_view
from django.urls import path


urlpatterns = [
    path("view_my_hostel/", ViewMyHostel.as_view(), name="view_my_hostel"),
    path("view_hostler/", Hostler_view.as_view(), name="view_my_hostler"),
]
