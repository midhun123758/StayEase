from unittest.mock import patch

from django.utils import timezone

from rest_framework.test import APITestCase
from rest_framework import status

from App.models import User

from Base_Panel.models import (
    Hostel,
    ChatRoom
)

from Client_panel.models import (
    Enquiry,
    HostelMessage
)


class ClientPanelTests(APITestCase):

    def setUp(self):

        self.owner = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="test123",
            role="owner"
        )

        self.client_user = User.objects.create_user(
            username="client",
            email="client@test.com",
            password="test123"
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

        self.chatroom = ChatRoom.objects.create(
            hostel=self.hostel,
            owner=self.owner,
            client=self.client_user
        )

        HostelMessage.objects.create(

            chatroom=self.chatroom,

            sender=self.client_user,

            receiver=self.owner,

            message="Hello Owner",

            message_type="text",

            is_read=False
        )

    # ==================================================
    # SEARCH HOSTEL TESTS
    # ==================================================

    def test_search_hostel_success(self):

        payload = {
            "latitude": 10.7867,
            "longitude": 76.6548
        }

        response = self.client.post(
            "/client/search/",
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertTrue(
            len(response.data) > 0
        )

    def test_search_hostel_no_results(self):

        payload = {
            "latitude": 0.0,
            "longitude": 0.0
        }

        response = self.client.post(
            "/client/search/",
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # ==================================================
    # HOSTEL DETAIL TESTS
    # ==================================================

    def test_hostel_detail_success(self):

        response = self.client.get(
            f"/client/hostel/{self.hostel.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_hostel_detail_not_found(self):

        response = self.client.get(
            "/client/hostel/999/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ==================================================
    # ENQUIRY TESTS
    # ==================================================

    @patch("Client_panel.views.async_to_sync")
    @patch("Client_panel.views.get_channel_layer")
    def test_create_enquiry_success(
        self,
        mock_channel_layer,
        mock_async_to_sync
    ):

        self.client.force_authenticate(
            user=self.client_user
        )

        payload = {
            "full_name": "Midhun",
            "email": "midhun@test.com",
            "phone": "9999999999",
            "preferred_date": str(
                timezone.now().date()
            ),
            "stay_months": 3,
            "message": "Interested"
        }

        response = self.client.post(
            f"/client/hostels/{self.hostel.id}/enquiry/",
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_create_enquiry_invalid_hostel(self):

        self.client.force_authenticate(
            user=self.client_user
        )

        payload = {
            "full_name": "Midhun",
            "email": "midhun@test.com",
            "phone": "9999999999",
            "preferred_date": str(
                timezone.now().date()
            ),
            "stay_months": 3,
            "message": "Interested"
        }

        response = self.client.post(
            "/client/hostels/999/enquiry/",
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ==================================================
    # USER DETAIL TESTS
    # ==================================================

    def test_user_detail_success(self):

        response = self.client.get(
            f"/client/api/user/{self.owner.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_user_detail_not_found(self):

        response = self.client.get(
            "/client/api/user/999/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    # ==================================================
    # CHAT HISTORY TESTS
    # ==================================================

    def test_chat_history_client(self):
        self.client.force_authenticate(
            user=self.client_user
        )
        response = self.client.get(
            f"/client/hostel/{self.hostel.id}/history/"
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_chat_history_owner(self):

        self.client.force_authenticate(
            user=self.owner
        )

        response = self.client.get(
            f"/client/hostel/{self.hostel.id}/history/?client_id={self.client_user.id}"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # ==================================================
    # CLIENT ENQUIRY LIST TESTS
    # ==================================================

    def test_client_enquiry_list(self):

        self.client.force_authenticate(
            user=self.client_user
        )

        Enquiry.objects.create(
            user=self.client_user,
            hostel=self.hostel,
            full_name="Midhun",
            email="midhun@test.com",
            phone="9999999999",
            preferred_date=timezone.now().date(),
            stay_months=3,
            message="Interested"
        )

        response = self.client.get(
            "/client/enquiry_view/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    # ==================================================
    # SECURITY TESTS
    # ==================================================

    def test_chat_history_unauthorized(self):

        response = self.client.get(
            f"/client/hostel/{self.hostel.id}/history/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_client_enquiry_list_unauthorized(self):

        response = self.client.get(
            "/client/enquiry_view/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )