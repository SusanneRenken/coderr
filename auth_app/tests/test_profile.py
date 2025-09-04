from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from auth_app.api.serializers import ProfileSerializer
from auth_app.models import Profile

class ProfileHappyPathTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        cls.other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='otherpassword'
        )
        cls.user_profile = Profile.objects.create(user=cls.user, type='customer')
        cls.other_profile = Profile.objects.create(user=cls.other_user, type='business')

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_own_profile(self):
        url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ProfileSerializer(self.user_profile).data)

    def test_get_other_profile(self):
        url = reverse('profile-detail', kwargs={'pk': self.other_profile.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, ProfileSerializer(self.other_profile).data)

    def test_get_profile_fields_empty(self):
        url = reverse('profile-detail', kwargs={'pk': self.user.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], '')
        self.assertEqual(response.data['last_name'], '')
        self.assertEqual(response.data['location'], '')
        self.assertEqual(response.data['tel'], '')
        self.assertEqual(response.data['description'], '')
        self.assertEqual(response.data['working_hours'], '')


class ProfileValidationTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        cls.user_profile = Profile.objects.create(user=cls.user, type='customer')

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_unknown_profile(self):
        url = reverse('profile-detail', kwargs={'pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProfilePermissionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        cls.user_profile = Profile.objects.create(user=cls.user, type='customer')

    def test_unauthenticated_user_get_profile(self):
        url = reverse('profile-detail', kwargs={'pk': self.user_profile.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    
