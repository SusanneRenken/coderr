from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from auth_app.models import Profile


class LoginHappyPathTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="user1", password="password1", email="user1@example.com")

    def test_login_success(self):
        url = reverse('login')
        data = {
            'username': 'user1',
            'password': 'password1'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')
        self.assertEqual(response.data['email'], 'user1@example.com')
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)
        self.assertTrue(response.data["token"])


class LoginValidationTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="user1", password="password1", email="user1@example.com")

    def test_login_no_username(self):
        url = reverse('login')
        data = {
            'password': 'password1'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unknown_user(self):
        url = reverse('login')
        data = {
            'username': 'unknownuser1',
            'password': 'password1'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_no_password(self):
        url = reverse('login')
        data = {
            'username': 'user1'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_wrong_password(self):
        url = reverse('login')
        data = {
            'username': 'user1',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
