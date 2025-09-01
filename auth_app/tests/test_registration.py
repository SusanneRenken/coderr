from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from auth_app.models import Profile


class RegistrationHappyPathTests(APITestCase):

    def test_create_user(self):
        url = reverse('registration')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'testuser@example.com')
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(Profile.objects.filter(user__username="testuser").count(), 1)
        self.assertIn("token", response.data)
        self.assertIn("user_id", response.data)
        self.assertTrue(response.data["token"])
        u = User.objects.get(username="testuser")
        self.assertNotEqual(u.password, "testpass123")
        self.assertTrue(u.check_password("testpass123"))

    def test_default_type_is_customer(self):
        url = reverse('registration')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())
        profile = Profile.objects.get(user__username='testuser')
        self.assertEqual(profile.type, 'customer')


class RegistrationValidationTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="user1", password="password1", email="user1@example.com")

    def test_create_no_username(self):
        url = reverse('registration')
        data = {
            'email': 'testuser2@example.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_email(self):
        url = reverse('registration')
        data = {
            'username': 'testuser2',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_no_password(self):
        url = reverse('registration')
        data = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'repeated_password': 'testpass123',
            'type': 'customer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_empty_username(self):
        url = reverse('registration')
        data = {
            'username': '',
            'email': 'testuser2@example.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_empty_email(self):
        url = reverse('registration')
        data = {
            'username': 'testuser2',
            'email': '',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_empty_password(self):
        url = reverse('registration')
        data = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password': '',
            'repeated_password': '',
            'type': 'customer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_mismatch(self):
        url = reverse('registration')
        data = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password': 'testpass123',
            'repeated_password': 'testpass456',
            'type': 'customer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("repeated_password", response.data)
        self.assertEqual(response.data["repeated_password"], [
                         "Passwords do not match."])

    def test_duplicate_email(self):
        url = reverse('registration')
        data = {
            'username': 'testuser2',
            'email': 'user1@example.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], ["Email already exists."])

    def test_duplicate_case_insensitive_email(self):
        url = reverse('registration')
        data = {
            'username': 'testuser2',
            'email': 'USER1@EXAMPLE.COM',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertEqual(response.data["email"], ["Email already exists."])

    def test_invalid_email_format(self):
        url = reverse('registration')
        data = {
            'username': 'testuser2',
            'email': 'not-an-email',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)


    def test_duplicate_username(self):
        url = reverse('registration')
        data = {
            'username': 'user1',
            'email': 'user2@example.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'customer'
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_invalid_type(self):
        url = reverse('registration')
        data = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password': 'testpass123',
            'repeated_password': 'testpass123',
            'type': 'invalid_type'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)

    def test_no_side_effects_on_error(self):
        url = reverse('registration')
        data = {
            'username': 'testuser2',
            'type': 'customer'
        }
        users_before = User.objects.count()
        profiles_before = Profile.objects.count()

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(User.objects.count(), users_before)
        self.assertEqual(Profile.objects.count(), profiles_before)
        
