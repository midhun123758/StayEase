from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from App.models import User
from Base_Panel.models import (
    Hostel,
    Room,
    Hostler,
    Transaction,
    MealTemplate,
    MessCharge,
    HostelDocument,
)
from Client_panel.models import Enquiry


ADD_HOSTEL_URL = "/hostel/add_hostel/"
ADD_ROOM_URL = "/hostel/add-room/"
ADD_HOSTLER_URL = "/hostel/add_hostler/"
MY_HOSTLERS_URL = "/hostel/my-hostlers/"
MEAL_TEMPLATE_URL = "/hostel/meal-templates/"
DAILY_MEAL_URL = "/hostel/daily-assignments/"
ENQUIRY_LIST_URL = "/hostel/enquiry-list/"
ENQUIRY_EDIT_URL = "/hostel/enquery_edit/"
FINANCE_URL = "/hostel/financial-overview/"
ADD_DOCUMENT_URL = "/hostel/add-document/"


def make_owner():
    return User.objects.create_user(
        username="owner",
        email="owner@test.com",
        password="123456",
        role="owner",
    )


def make_client():
    return User.objects.create_user(
        username="client",
        email="client@test.com",
        password="123456",
        role="user",
    )


def make_hostel(owner, name="StayEase Hostel"):
    return Hostel.objects.create(
        owner=owner,
        name=name,
        address="Palakkad",
        location="Palakkad Town",
        latitude=10.7867,
        longitude=76.6548,
        city="Palakkad",
        state="Kerala",
        description="Good hostel",
        rooms_available=5,
        mess_service=True,
        contact_number="9876543210",
    )


def make_room(hostel, room_number="101"):
    return Room.objects.create(
        hostel=hostel,
        room_number=room_number,
        room_type="single",
        price=5000,
        is_available=True,
        bed_space=2,
    )


def make_meal(hostel, name="Idli"):
    return MealTemplate.objects.create(
        hostel=hostel,
        name=name,
        default_meal_type="BRK",
        is_deleted=False,
    )


def make_hostler(
    owner,
    hostel,
    room,
    username="hostler",
    email="hostler@test.com",
):
    user = User.objects.create_user(
        username=username,
        email=email,
        password="123456",
        role="hostler",
        owner=owner,
    )

    return Hostler.objects.create(
        user=user,
        owner=owner,
        hostel=hostel,
        room=room,
        phone="9876543210",
        parent_number="9876543211",
        monthly_rent=5000,
        check_in_date=timezone.now().date(),
        check_out_date=None,
        is_active=True,
    )


class BasePanelAPITest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.owner = make_owner()
        self.client.force_authenticate(user=self.owner)

        self.hostel = make_hostel(self.owner)
        self.room = make_room(self.hostel)
        self.meal = make_meal(self.hostel)

    def test_add_hostel(self):
        data = {
            "name": "New Hostel",
            "address": "Kochi",
            "location": "Edappally",
            "latitude": 10.0261,
            "longitude": 76.3125,
            "city": "Kochi",
            "state": "Kerala",
            "description": "Nice hostel",
            "rooms_available": 10,
            "mess_service": True,
            "contact_number": "9876543210",
        }

        response = self.client.post(
            ADD_HOSTEL_URL,
            data,
            format="multipart"
        )

        self.assertIn(response.status_code, [201, 403])

    def test_add_room(self):
        data = {
            "room_number": "102",
            "room_type": "double",
            "price": "6000.00",
            "is_available": True,
            "bed_space": 2,
        }

        response = self.client.post(
            f"{ADD_ROOM_URL}?hostel_id={self.hostel.id}",
            data,
            format="multipart"
        )

        self.assertEqual(response.status_code, 201)

    def test_add_hostler(self):
        data = {
            "username": "newhostler",
            "email": "newhostler@test.com",
            "phone": "9876543210",
            "parent_number": "9876543211",
            "hostel": self.hostel.id,
            "room": self.room.id,
            "monthly_rent": "5000.00",
            "check_in_date": str(timezone.now().date()),
        }

        response = self.client.post(
            ADD_HOSTLER_URL,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201,
            msg=response.data
        )
        self.assertEqual(Transaction.objects.count(), 1)

    def test_my_hostlers_list(self):
        make_hostler(self.owner, self.hostel, self.room)

        response = self.client.get(
            f"{MY_HOSTLERS_URL}?hostel_id={self.hostel.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_meal_template(self):
        data = {
            "hostel": self.hostel.id,
            "name": "Dosa",
            "default_meal_type": "BRK",
        }

        response = self.client.post(
            MEAL_TEMPLATE_URL,
            data,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            201,
            msg=response.data
        )

    def test_daily_meal_assignment(self):
        make_hostler(self.owner, self.hostel, self.room)

        data = {
            "hostel": self.hostel.id,
            "meal_item": self.meal.id,
            "date": str(timezone.now().date()),
            "meal_type": "BRK",
            "amount_per_hostler": "50.00",
            "description": "Morning food",
        }

        response = self.client.post(
            DAILY_MEAL_URL,
            data,
            format="multipart"
        )

        self.assertIn(response.status_code, [200, 201])
        self.assertEqual(MessCharge.objects.count(), 1)

    def test_enquiry_list(self):
        client_user = make_client()

        Enquiry.objects.create(
            hostel=self.hostel,
            user=client_user,
            full_name="Test Client",
            email="client@test.com",
            phone="9876543210",
            preferred_date=timezone.now().date(),
            stay_months=2,
            message="I am interested",
            status="pending",
        )

        response = self.client.get(
            f"{ENQUIRY_LIST_URL}?hostel_id={self.hostel.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_enquiry_accept(self):
        client_user = make_client()

        enquiry = Enquiry.objects.create(
            hostel=self.hostel,
            user=client_user,
            full_name="Test Client",
            email="client@test.com",
            phone="9876543210",
            preferred_date=timezone.now().date(),
            stay_months=2,
            message="I am interested",
            status="pending",
        )

        response = self.client.patch(
            f"{ENQUIRY_EDIT_URL}{enquiry.id}/",
            {"status": "accepted by owner"},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, "accepted by owner")

    def test_enquiry_reject_with_reason(self):
        client_user = make_client()

        enquiry = Enquiry.objects.create(
            hostel=self.hostel,
            user=client_user,
            full_name="Test Client",
            email="client@test.com",
            phone="9876543210",
            preferred_date=timezone.now().date(),
            stay_months=2,
            message="I am interested",
            status="pending",
        )

        response = self.client.patch(
            f"{ENQUIRY_EDIT_URL}{enquiry.id}/",
            {
                "status": "rejected",
                "rejection_reason": "Room is not available",
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, "rejected")
        self.assertEqual(
            enquiry.rejection_reason,
            "Room is not available"
        )

    def test_financial_overview(self):
        hostler = make_hostler(
            self.owner,
            self.hostel,
            self.room,
            username="financehostler",
            email="finance@test.com"
        )

        Transaction.objects.create(
            hostler=hostler,
            amount=5000,
            status="pending",
        )

        response = self.client.get(
            f"{FINANCE_URL}?hostel={self.hostel.id}"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("summary", response.data)
        self.assertEqual(response.data["summary"]["pending"], 5000)

    def test_add_document(self):
        data = {
            "hostel": self.hostel.id,
            "file_url": "https://example.com/test.pdf",
            "document_type": "license",
        }

        response = self.client.post(
            ADD_DOCUMENT_URL,
            data,
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(HostelDocument.objects.count(), 1)