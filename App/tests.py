

# Create your tests here.
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class AuthTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.signup_url = '/auth/signup/'
        self.login_url = '/auth/login/'

    def test_signup(self):
        data = {
            "username": "mithun",
            "email": "mithun@gmail.com",
            "password": "1234"
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        # create user first
        User.objects.create_user(
            username="mithun",
            email="mithun@gmail.com",
            password="1234"
        )

        data = {
            "email": "mithun@gmail.com",
            "password": "1234"
        }

        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)