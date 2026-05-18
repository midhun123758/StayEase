from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch

from rest_framework_simplejwt.tokens import RefreshToken

from django.utils import timezone
from datetime import timedelta

from App.models import (
    User,
    PasswordResetOTP,
    KycDocument
)


class AdvancedAuthTests(APITestCase):

    def setUp(self):

        self.signup_url = "/auth/signup/"
        self.login_url = "/auth/login/"
        self.owner_signup_url = "/auth/owner/signup/"
        self.google_login_url = "/auth/google/login/"
        self.send_otp_url = "/auth/send-otp/"
        self.verify_otp_url = "/auth/verify-otp/"
        self.reset_password_url = "/auth/reset-password/"
        self.logout_url = "/auth/logout/"
        self.kyc_url = "/auth/kyc/"

        self.user = User.objects.create_user(
            username="midhun",
            email="midhun@test.com",
            password="test123",
        )

        self.google_user = User.objects.create_user(
            username="googleuser",
            email="google@test.com",
            password="test123",
            is_google_user=True
        )

    # ==========================================
    # SIGNUP TESTS
    # ==========================================

    def test_signup_success(self):

        payload = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "test123",
            "phone": "+917559976674"
        }

        response = self.client.post(
            self.signup_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            User.objects.filter(
                email="new@test.com"
            ).exists()
        )

    def test_signup_duplicate_email(self):

        payload = {
            "username": "duplicate",
            "email": "midhun@test.com",
            "password": "test123"
        }

        response = self.client.post(
            self.signup_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_signup_invalid_email(self):

        payload = {
            "username": "invalid",
            "email": "not-an-email",
            "password": "test123"
        }

        response = self.client.post(
            self.signup_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_signup_empty_password(self):

        payload = {
            "username": "empty",
            "email": "empty@test.com",
            "password": ""
        }

        response = self.client.post(
            self.signup_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==========================================
    # OWNER SIGNUP
    # ==========================================

    def test_owner_signup_success(self):

        payload = {
            "username": "owner",
            "email": "owner@test.com",
            "password": "test123"
        }

        response = self.client.post(
            self.owner_signup_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        user = User.objects.get(
            email="owner@test.com"
        )

        self.assertEqual(user.role, "owner")
        self.assertTrue(user.is_staff)

    def test_owner_signup_duplicate_email(self):

        payload = {
            "username": "owner",
            "email": "midhun@test.com",
            "password": "test123"
        }

        response = self.client.post(
            self.owner_signup_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==========================================
    # LOGIN TESTS
    # ==========================================

    @patch("App.views.verify_captcha")
    def test_login_success(self, mock_captcha):

        mock_captcha.return_value = True

        payload = {
            "email": "midhun@test.com",
            "password": "test123",
            "captcha": "valid"
        }

        response = self.client.post(
            self.login_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    @patch("App.views.verify_captcha")
    def test_login_wrong_password(self, mock_captcha):

        mock_captcha.return_value = True

        payload = {
            "email": "midhun@test.com",
            "password": "wrong",
            "captcha": "valid"
        }

        response = self.client.post(
            self.login_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    @patch("App.views.verify_captcha")
    def test_login_google_user_with_password(self, mock_captcha):

        mock_captcha.return_value = True

        payload = {
            "email": "google@test.com",
            "password": "test123",
            "captcha": "valid"
        }

        response = self.client.post(
            self.login_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    @patch("App.views.verify_captcha")
    def test_login_invalid_captcha(self, mock_captcha):

        mock_captcha.return_value = False

        payload = {
            "email": "midhun@test.com",
            "password": "test123",
            "captcha": "bad"
        }

        response = self.client.post(
            self.login_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    @patch("App.views.verify_captcha")
    def test_login_missing_fields(self, mock_captcha):

        mock_captcha.return_value = True

        payload = {
            "email": ""
        }

        response = self.client.post(
            self.login_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==========================================
    # GOOGLE LOGIN
    # ==========================================

    @patch("App.views.requests.get")
    def test_google_login_success(self, mock_get):

        mock_get.return_value.status_code = 200

        mock_get.return_value.json.return_value = {
            "email": "newgoogle@test.com",
            "name": "Google User",
            "email_verified": True
        }

        payload = {
            "token": "google-token"
        }

        response = self.client.post(
            self.google_login_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    @patch("App.views.requests.get")
    def test_google_login_invalid_token(self, mock_get):

        mock_get.return_value.status_code = 400

        payload = {
            "token": "invalid"
        }

        response = self.client.post(
            self.google_login_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    @patch("App.views.requests.get")
    def test_google_login_unverified_email(self, mock_get):

        mock_get.return_value.status_code = 200

        mock_get.return_value.json.return_value = {
            "email": "fake@test.com",
            "email_verified": False
        }

        payload = {
            "token": "token"
        }

        response = self.client.post(
            self.google_login_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==========================================
    # OTP TESTS
    # ==========================================

    def test_send_otp_success(self):

        payload = {
            "email": "midhun@test.com"
        }

        response = self.client.post(
            self.send_otp_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_send_otp_invalid_email(self):

        payload = {
            "email": "unknown@test.com"
        }

        response = self.client.post(
            self.send_otp_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_verify_otp_success(self):

        otp = PasswordResetOTP.objects.create(
            user=self.user,
            otp="123456"
        )

        payload = {
            "email": "midhun@test.com",
            "otp": "123456"
        }

        response = self.client.post(
            self.verify_otp_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_verify_otp_expired(self):

        otp = PasswordResetOTP.objects.create(
            user=self.user,
            otp="123456"
        )

        otp.created_at = timezone.now() - timedelta(minutes=10)
        otp.save()

        payload = {
            "email": "midhun@test.com",
            "otp": "123456"
        }

        response = self.client.post(
            self.verify_otp_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==========================================
    # RESET PASSWORD
    # ==========================================

    def test_reset_password_success(self):

        PasswordResetOTP.objects.create(
            user=self.user,
            otp="123456",
            is_verified=True
        )

        payload = {
            "email": "midhun@test.com",
            "new_password": "newpassword123",
            "confirm_password": "newpassword123"
        }

        response = self.client.post(
            self.reset_password_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

    def test_reset_password_mismatch(self):

        payload = {
            "email": "midhun@test.com",
            "new_password": "123",
            "confirm_password": "456"
        }

        response = self.client.post(
            self.reset_password_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    # ==========================================
    # LOGOUT
    # ==========================================

    def test_logout_success(self):

        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        payload = {
            "refresh": str(refresh)
        }

        response = self.client.post(
            self.logout_url,
            payload,
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_205_RESET_CONTENT
        )

    # ==========================================
    # KYC TESTS
    # ==========================================

    def test_kyc_without_authentication(self):

        response = self.client.post(
            self.kyc_url,
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )