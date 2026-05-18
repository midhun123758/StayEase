from unittest.mock import patch

from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from App.models import User

from Base_Panel.models import (
    Hostel,
    Room,
    Hostler,
    OwnerSubscription,
    MealTemplate,
    Transaction,
    ChatRoom,
)

from Client_panel.models import Enquiry


class BasePanelTests(APITestCase):

    def setUp(self):

        self.owner = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="test123",
            role="owner"
        )

        self.other_owner = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="test123",
            role="owner"
        )

        self.client.force_authenticate(
            user=self.owner
        )

        self.hostel = Hostel.objects.create(
            owner=self.owner,
            name="StayEase Hostel",
            address="Palakkad",
            location="Palakkad",
            latitude=10.7867,
            longitude=76.6548,
            city="Palakkad",
            state="Kerala",
            contact_number="7559976674"
        )

        self.room = Room.objects.create(
            hostel=self.hostel,
            room_number="101",
            room_type="AC",
            price=2500,
            bed_space=2
        )

        OwnerSubscription.objects.create(
            owner=self.owner,
            plan="FREE",
            hostel_limit=1
        )

    # ==================================================
    # HOSTEL TESTS
    # ==================================================

    def test_edit_hostel(self):

        # Edit_hostel.patch() reads hostel_id from GET params
        payload = {
            "name": "Updated Hostel",
            "address": "Updated Address",
            "location": "Palakkad",
            "latitude": 10.7867,
            "longitude": 76.6548,
            "city": "Palakkad",
            "state": "Kerala",
            "contact_number": "9999999999",
        }

        response = self.client.patch(
            f"/hostel/edit_hostel/?hostel_id={self.hostel.id}",
            payload,
            format="json"
        )

        self.assertIn(
            response.status_code,
            [200, 201]
        )

    # ==================================================
    # ROOM TESTS
    # ==================================================

    def test_room_creation(self):

        # FIX 1 — pass hostel_id as query param, not in body
        payload = {
            "room_number": "102",
            "room_type": "NON AC",
            "price": 3000,
            "bed_space": 3
        }

        response = self.client.post(
            f"/hostel/add-room/?hostel_id={self.hostel.id}",
            payload
        )

        self.assertIn(
            response.status_code,
            [200, 201]
        )

    def test_room_list(self):

        # Room_listView.get() reads hostel_id, not hostel
        response = self.client.get(
            f"/hostel/room-list/?hostel_id={self.hostel.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # ==================================================
    # HOSTLER TESTS
    # ==================================================

    def test_add_hostler(self):

        payload = {
            "username": "hostler1",
            "email": "hostler@test.com",
            "hostel": self.hostel.id,
            "room": self.room.id,
            "monthly_rent": 2500,
            "phone": "9999999999",
            "check_in_date": str(
                timezone.now().date()
            )
        }

        response = self.client.post(
            "/hostel/add_hostler/",
            payload,
            format="json"
        )

        self.assertIn(
            response.status_code,
            [200, 201]
        )

    def test_room_capacity_exceeded(self):

        for i in range(2):

            user = User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@test.com",
                password="test123"
            )

            Hostler.objects.create(
                user=user,
                owner=self.owner,
                hostel=self.hostel,
                room=self.room,
                phone="9999999999",
                monthly_rent=2500,
                check_in_date=timezone.now().date()
            )

        payload = {
            "username": "overflow",
            "email": "overflow@test.com",
            "hostel": self.hostel.id,
            "room": self.room.id,
            "monthly_rent": 2500,
            "phone": "9999999999",
            "check_in_date": str(
                timezone.now().date()
            )
        }

        response = self.client.post(
            "/hostel/add_hostler/",
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_my_hostlers(self):

        # my_hostlers.get() filters by hostel_id query param
        response = self.client.get(
            f"/hostel/my-hostlers/?hostel_id={self.hostel.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # ==================================================
    # MEAL TESTS
    # ==================================================

    def test_create_meal_template(self):

        payload = {
            "hostel": self.hostel.id,
            "name": "Biriyani",
            "default_meal_type": "DIN"
        }

        response = self.client.post(
            "/hostel/meal-templates/",
            payload,
            format="json"
        )

        self.assertIn(
            response.status_code,
            [200, 201]
        )

    def test_get_meals(self):

        MealTemplate.objects.create(
            hostel=self.hostel,
            name="Meals",
            default_meal_type="LNC"
        )

        response = self.client.get(
            f"/hostel/meal-templates/?hostel={self.hostel.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_daily_assignment(self):

        meal = MealTemplate.objects.create(
            hostel=self.hostel,
            name="Chicken Curry",
            default_meal_type="DIN"
        )

        payload = {
            "hostel": self.hostel.id,
            "meal_item": meal.id,
            "date": str(timezone.now().date()),
            "meal_type": "DIN",
            "amount_per_hostler": 100
        }

        response = self.client.post(
            "/hostel/daily-assignments/",
            payload,
            format="json"
        )

        self.assertIn(
            response.status_code,
            [200, 201]
        )

    # ==================================================
    # ENQUIRY TESTS
    # ==================================================

    def test_enquiry_list(self):

        # EnquiryListView.get() filters by hostel_id query param
        response = self.client.get(
            f"/hostel/enquiry-list/?hostel_id={self.hostel.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_invalid_enquiry_status(self):

        enquiry = Enquiry.objects.create(
            user=self.owner,
            hostel=self.hostel,
            full_name="Midhun",
            email="midhun@test.com",
            phone="9999999999",
            preferred_date=timezone.now().date(),
            stay_months=3,
            message="Interested"
        )

        payload = {
            "status": "INVALID"
        }

        response = self.client.patch(
            f"/hostel/enquery_edit/{enquiry.id}/",
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==================================================
    # FINANCIAL TESTS
    # ==================================================

    def test_financial_overview(self):

        user = User.objects.create_user(
            username="hostler",
            email="hostler@test.com",
            password="test123"
        )

        hostler = Hostler.objects.create(
            user=user,
            owner=self.owner,
            hostel=self.hostel,
            room=self.room,
            phone="9999999999",
            monthly_rent=2500,
            check_in_date=timezone.now().date()
        )

        Transaction.objects.create(
            hostler=hostler,
            owner=self.owner,
            amount=2500,
            status="pending"
        )

        response = self.client.get(
            f"/hostel/financial-overview/?hostel={self.hostel.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # ==================================================
    # SUBSCRIPTION TESTS
    # ==================================================

    def test_subscription_detail(self):

        response = self.client.get(
            "/hostel/subscription/detail/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    @patch("Base_Panel.views.razorpay.Client")
    def test_verify_subscription_payment(
        self,
        mock_client
    ):

        mock_client.return_value.utility.verify_payment_signature.return_value = True

        payload = {
            "razorpay_order_id": "order123",
            "razorpay_payment_id": "payment123",
            "razorpay_signature": "signature",
            "plan": "PRO"
        }

        response = self.client.post(
            "/hostel/subscription/verify-payment/",
            payload,
            format="json"
        )

        self.assertIn(
            response.status_code,
            [200, 201]
        )

    # ==================================================
    # OWNER PROFILE
    # ==================================================

    def test_owner_profile(self):

        # Owner_Profile.get() requires ?id= query param
        response = self.client.get(
            f"/hostel/owner_profile/?id={self.owner.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # ==================================================
    # ROOM IMAGE VIEW
    # ==================================================

    def test_room_images_view(self):

        # RoomImagesListView.get() reads ?hostel= not ?room_id=
        response = self.client.get(
            f"/hostel/image_view/?hostel={self.hostel.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # ==================================================
    # CHATROOM TESTS
    # ==================================================

    def test_chatrooms(self):

        # OwnerChatListView.get() requires ?hostel_id=
        # and returns 400 if missing — create a room first
        ChatRoom.objects.create(
            hostel=self.hostel,
            owner=self.owner,
            client=self.other_owner
        )

        response = self.client.get(
            f"/hostel/chatrooms/?hostel_id={self.hostel.id}"
        )

        self.assertIn(
            response.status_code,
            [200, 204]
        )

    # ==================================================
    # SECURITY TESTS
    # ==================================================

    def test_unauthorized_access(self):

        self.client.force_authenticate(
            user=None
        )

        response = self.client.get(
            f"/hostel/financial-overview/?hostel={self.hostel.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )