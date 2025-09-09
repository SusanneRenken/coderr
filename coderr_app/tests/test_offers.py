from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from auth_app.models import Profile

class OffersHappyPathTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        cls.user_profile = Profile.objects.create(user=cls.user, type='business')

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_create_offer(self):
        url =  reverse('offer-list')
        data = {
            'title': 'Test Offer',
            'description': 'This is a test offer'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
