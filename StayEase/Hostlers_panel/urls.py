

from .views import GPayPaymentView, ViewMyHostel,Hostler_view, my_room,PaymentsView,CreatePayment,VerifyPayment
from django.urls import path

urlpatterns = [
    path("view_my_hostel/", ViewMyHostel.as_view(), name="view_my_hostel"),
    path("view_hostler/", Hostler_view.as_view(), name="view_my_hostler"),
    path("hostler_transactions/", PaymentsView.as_view(), name="my_transactions "),
    path("create-payment/",CreatePayment.as_view()),
    path("verify-payment/",VerifyPayment.as_view()),
    path("my_room/",my_room.as_view(),name="my_room"),
    path("gpay-payment/<int:transaction_id>/",GPayPaymentView.as_view()
),
]
