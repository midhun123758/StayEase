from django.urls import re_path

from .consumers import RoomGroupConsumer

websocket_urlpatterns = [

    re_path(
        r"ws/group-chat/(?P<group_id>\d+)/$",
        RoomGroupConsumer.as_asgi()
    ),

]