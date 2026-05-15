from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from App.models import User
from Base_Panel.models import Hostel, Room, Hostler, Transaction


HOSTLER_VIEW_URL = "/hostler/view_hostler/"
MY_HOSTEL_URL = "/hostler/view_my_hostel/"
PAYMENTS_URL = "/hostler/hostler_transactions/"
MY_ROOM_URL = "/hostler/my_room/"


def make_owner():
    return User.objects.create_user(
        username="owner",
        email="owner@test.com",
        password="123456",
        role="owner",
    )


def make_hostler_user():
    return User.objects.create_user(
        username="hostler",
        email="hostler@test.com",
        password="123456",
        role="hostler",
    )


def make_hostel(owner):
    return Hostel.objects.create(
        owner=owner,
        name="StayEase Hostel",
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


def make_room(hostel):
    return Room.objects.create(
        hostel=hostel,
        room_number="101",
        room_type="AC",
        price=2500,
        is_available=False,
        bed_space=4,
    )


def make_hostler(user, owner, hostel, room):
    return Hostler.objects.create(
        user=user,
        owner=owner,
        hostel=hostel,
        room=room,
        phone="7559976674",
        parent_number="8556693214",
        monthly_rent=2500,
        check_in_date=timezone.now().date(),
        is_active=True,
    )


class HostlerPanelAPITest(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.owner = make_owner()
        self.hostler_user = make_hostler_user()
        self.hostel = make_hostel(self.owner)
        self.room = make_room(self.hostel)

        self.hostler = make_hostler(
            user=self.hostler_user,
            owner=self.owner,
            hostel=self.hostel,
            room=self.room,
        )

        self.client.force_authenticate(user=self.hostler_user)

    def test_hostler_view(self):
        response = self.client.get(HOSTLER_VIEW_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["phone"], "7559976674")

    def test_view_my_hostel(self):
        response = self.client.get(MY_HOSTEL_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "StayEase Hostel")

    def test_hostler_transactions(self):
        Transaction.objects.create(
            hostler=self.hostler,
            owner=self.owner,
            amount=2500,
            status="pending",
        )

        response = self.client.get(PAYMENTS_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(str(response.data[0]["amount"]), "2500.00")

    def test_my_room(self):
        response = self.client.get(MY_ROOM_URL)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["room"]["room_number"], "101")
        self.assertEqual(response.data["room"]["room_type"], "AC")
        self.assertEqual(response.data["room"]["bed_space"], 4)

    def test_my_room_without_room(self):
        self.hostler.room = None
        self.hostler.save()

        response = self.client.get(MY_ROOM_URL)

        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_cannot_access(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(MY_ROOM_URL)

        self.assertEqual(response.status_code, 401)