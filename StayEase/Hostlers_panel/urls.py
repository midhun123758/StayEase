

from .views import GPayPaymentView, MyRoomChatView, ReactMealView, RespondMealView, RoomChatMessagesView, TodayMealsView, ViewMyHostel,Hostler_view, my_room,PaymentsView,CreatePayment,VerifyPayment
from django.urls import path

urlpatterns = [
    path("view_my_hostel/", ViewMyHostel.as_view(), name="view_my_hostel"),
    path("view_hostler/", Hostler_view.as_view(), name="view_my_hostler"),
    path("hostler_transactions/", PaymentsView.as_view(), name="my_transactions "),
    path("create-payment/",CreatePayment.as_view()),
    path("verify-payment/",VerifyPayment.as_view()),
    path("my_room/",my_room.as_view(),name="my_room"),
    path("gpay-payment/<int:transaction_id>/",GPayPaymentView.as_view()),
    path("room-chat/<int:group_id>/messages/",RoomChatMessagesView.as_view()),
    path("my-room-chat/",MyRoomChatView.as_view(),name="my_room_chat",),
    path("respond-meal/",RespondMealView.as_view()),
    path("today-meals/",TodayMealsView.as_view()),
    path("react-meal/",ReactMealView.as_view()

),
]
