from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from Base_Panel.models import Hostel, Room, Hostler
from Hostlers_panel.models import RoomChatGroup, RoomChatMessage

User = get_user_model()


class RoomChatSystemTest(TestCase):

    def setUp(self):

        self.client = APIClient()

        # ---------------------------------------------------
        # CREATE OWNER
        # ---------------------------------------------------

        self.owner = User.objects.create_user(
            username="owner",
            email="owner@test.com",
            password="123456"
        )

        # ---------------------------------------------------
        # CREATE HOSTEL
        # ---------------------------------------------------

        self.hostel = Hostel.objects.create(
            owner=self.owner,
            name="Green Valley Hostel",
            address="Palakkad",
            latitude=10.7867,
            longitude=76.6548,
            city="Palakkad",
            state="Kerala",
            contact_number="9876543210"
        )

        # ---------------------------------------------------
        # CREATE ROOM
        # ---------------------------------------------------

        self.room = Room.objects.create(
            hostel=self.hostel,
            room_number="101",
            room_type="Shared",
            price=2500,
            is_available=True
        )

        # ---------------------------------------------------
        # CREATE USERS
        # ---------------------------------------------------

        self.user1 = User.objects.create_user(
            username="midhun",
            email="midhun@test.com",
            password="123456"
        )

        self.user2 = User.objects.create_user(
            username="rahul",
            email="rahul@test.com",
            password="123456"
        )

        # ---------------------------------------------------
        # CREATE HOSTLERS
        # ---------------------------------------------------

        self.hostler1 = Hostler.objects.create(
            owner=self.owner,      # <-- FIX 1: Added Owner
            user=self.user1,
            hostel=self.hostel,
            room=self.room,
            is_active=True,
            check_in_date="2026-05-17",
            joining_date="2026-05-17",
            monthly_rent=2500
        )

        self.hostler2 = Hostler.objects.create(
            owner=self.owner,      # <-- FIX 1: Added Owner
            user=self.user2,
            hostel=self.hostel,
            room=self.room,
            is_active=True,
            check_in_date="2026-05-17",
            joining_date="2026-05-17",
            monthly_rent=2500
        )

        # ---------------------------------------------------
        # CREATE ROOM CHAT GROUP
        # ---------------------------------------------------
        
        # <-- FIX 2: Using get_or_create because a Signal likely already created it
        self.group, created = RoomChatGroup.objects.get_or_create(
            room=self.room,
            defaults={
                'hostel': self.hostel
            }
        )

        # ---------------------------------------------------
        # ADD MEMBERS
        # ---------------------------------------------------

        self.group.members.add(
            self.hostler1,
            self.hostler2
        )

    # ---------------------------------------------------
    # ROOM GROUP TEST
    # ---------------------------------------------------

    def test_room_group_created(self):

        self.assertEqual(
            self.group.room.room_number,
            "101"
        )

    # ---------------------------------------------------
    # MEMBER TEST
    # ---------------------------------------------------

    def test_members_added(self):

        self.assertEqual(
            self.group.members.count(),
            2
        )

    # ---------------------------------------------------
    # MESSAGE TEST
    # ---------------------------------------------------

    def test_send_message(self):

        message = RoomChatMessage.objects.create(
            group=self.group,
            sender=self.user1,
            message="Hello Roommates"
        )

        self.assertEqual(
            message.message,
            "Hello Roommates"
        )

    # ---------------------------------------------------
    # ACCESS TEST
    # ---------------------------------------------------

    def test_chat_access(self):

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            f"/hostler/room-chat/{self.group.id}/messages/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    # ---------------------------------------------------
    # SECURITY TEST
    # ---------------------------------------------------

    def test_block_other_room_users(self):

        outsider = User.objects.create_user(
            username="outsider",
            email="outsider@test.com",
            password="123456"
        )

        outsider_hostler = Hostler.objects.create(
            owner=self.owner,      # <-- FIX 1: Added Owner
            user=outsider,
            hostel=self.hostel,
            is_active=True,
            check_in_date="2026-05-17",
            joining_date="2026-05-17",
            monthly_rent=2500
        )

        self.client.force_authenticate(
            user=outsider
        )

        response = self.client.get(
            f"/hostler/room-chat/{self.group.id}/messages/"
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # ---------------------------------------------------
    # MY ROOM CHAT API TEST
    # ---------------------------------------------------

    def test_get_my_room_chat(self):

        self.client.force_authenticate(
            user=self.user1
        )

        response = self.client.get(
            "/hostler/my-room-chat/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["group_id"],
            self.group.id
        )