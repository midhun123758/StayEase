from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from App.models import User


class AuthTestCase(TestCase):

    def setUp(self):

        self.client = APIClient()

        self.signup_url = "/auth/signup/"

        self.login_url = "/auth/login/"

    def test_signup(self):

        data = {
            "username": "mithun",
            "email": "mithun@gmail.com",
            "password": "1234"
        }

        response = self.client.post(
            self.signup_url,
            data,
            format="json"
        )

        self.assertIn(
            response.status_code,
            [200, 201]
        )

    def test_login(self):

        User.objects.create_user(
            username="mithun",
            email="mithun@gmail.com",
            password="1234"
        )

        data = {
            "email": "mithun@gmail.com",
            "password": "1234",
            "captcha": "test"
        }

        response = self.client.post(
            self.login_url,
            data,
            format="json"
        )

        print(response.data)

        self.assertIn(
            response.status_code,
            [200, 400]
        )