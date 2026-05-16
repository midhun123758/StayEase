from datetime import date
from unittest.mock import patch

from rest_framework.test import APITestCase
from rest_framework import status

from App.models import User
from Base_Panel.models import (
    Hostel,
    Room,
    Hostler,
    Transaction
)


class HostlerViewsTest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="midhun",
            email="midhun@gmail.com",
            password="123456",
            role="hostler"
        )

        self.owner = User.objects.create_user(
            username="owner",
            email="owner@gmail.com",
            password="123456",
            role="owner"
        )

        self.hostel = Hostel.objects.create(
            owner=self.owner,
            name="StayEase Hostel",
            address="Palakkad",
            location="Town",
            latitude=10.7867,
            longitude=76.6548,
            city="Palakkad",
            state="Kerala",
            description="Good Hostel",
            rooms_available=5,
            mess_service=True,
            contact_number="9876543210"
        )

        self.room = Room.objects.create(
            hostel=self.hostel,
            room_number="101",
            room_type="single",
            price=2500,
            is_available=True,
            bed_space=2
        )

        self.hostler = Hostler.objects.create(
            user=self.user,
            owner=self.owner,
            hostel=self.hostel,
            room=self.room,
            phone="9876543210",
            parent_number="9999999999",
            monthly_rent=2500,
            check_in_date=date.today(),
            is_active=True
        )

        self.client.force_authenticate(
            user=self.user
        )

    # HOSTLER PROFILE

    def test_hostler_view(self):

        response = self.client.get(
            "/hostler/view_hostler/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # VIEW HOSTEL

    def test_view_my_hostel(self):

        response = self.client.get(
            "/hostler/view_my_hostel/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # VIEW ROOM

    def test_my_room(self):

        response = self.client.get(
            "/hostler/my_room/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # PAYMENTS VIEW

    def test_payments_view(self):

        Transaction.objects.create(
            hostler=self.hostler,
            owner=self.owner,
            amount=2500,
            status="paid"
        )

        response = self.client.get(
            "/hostler/hostler_transactions/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

    # CREATE PAYMENT

    @patch(
        "Hostlers_panel.views.client.order.create"
    )
    def test_create_payment(
        self,
        mock_order
    ):

        mock_order.return_value = {
            "id": "order_123"
        }

        response = self.client.post(
            "/hostler/create-payment/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data["success"],
            True
        )

    # DUPLICATE PAYMENT

    @patch(
        "Hostlers_panel.views.client.order.create"
    )
    def test_duplicate_payment(
        self,
        mock_order
    ):

        Transaction.objects.create(
            hostler=self.hostler,
            owner=self.owner,
            amount=2500,
            status="pending"
        )

        response = self.client.post(
            "/hostler/create-payment/"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # VERIFY PAYMENT

    @patch(
        "Hostlers_panel.views.client.utility.verify_payment_signature"
    )
    def test_verify_payment(
        self,
        mock_verify
    ):

        Transaction.objects.create(
            hostler=self.hostler,
            owner=self.owner,
            amount=2500,
            razorpay_order_id="order_123",
            status="pending"
        )

        response = self.client.post(
            "/hostler/verify-payment/",
            {
                "razorpay_order_id": "order_123",
                "razorpay_payment_id": "pay_123",
                "razorpay_signature": "signature_123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    # PAYMENT ALREADY VERIFIED

    @patch(
        "Hostlers_panel.views.client.utility.verify_payment_signature"
    )
    def test_payment_already_verified(
        self,
        mock_verify
    ):

        Transaction.objects.create(
            hostler=self.hostler,
            owner=self.owner,
            amount=2500,
            razorpay_order_id="order_123",
            status="paid"
        )

        response = self.client.post(
            "/hostler/verify-payment/",
            {
                "razorpay_order_id": "order_123",
                "razorpay_payment_id": "pay_123",
                "razorpay_signature": "signature_123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # INVALID TRANSACTION

    def test_invalid_transaction(self):

        response = self.client.post(
            "/hostler/verify-payment/",
            {
                "razorpay_order_id": "wrong",
                "razorpay_payment_id": "pay_123",
                "razorpay_signature": "signature_123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    # NO ROOM ASSIGNED

    def test_no_room_assigned(self):

        self.hostler.room = None

        self.hostler.save()

        response = self.client.get(
            "/hostler/my_room/"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    # NO HOSTEL ASSIGNED

    def test_no_hostel_assigned(self):

        self.hostler.hostel = None

        self.hostler.save()

        response = self.client.get(
            "/hostler/view_my_hostel/"
        )

        self.assertEqual(
            response.status_code,
            404
        )

    # UNAUTHORIZED USER

    def test_unauthorized_user(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            "/hostler/view_hostler/"
        )

        self.assertEqual(
            response.status_code,
            401
        )