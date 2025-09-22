from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Review

class OrderHappyTests(APITestCase):

    @classmethod
    def setUpTestData(cls):

        cls.business_user_1 = User.objects.create_user(
            username="business_user_1", email="business_user_1@example.com", password="x"
        )
        Profile.objects.create(user=cls.business_user_1, type="business")

        cls.business_user_2 = User.objects.create_user(
            username="business_user_2", email="business_user_2@example.com", password="x"
        )
        Profile.objects.create(user=cls.business_user_2, type="business")

        cls.customer_user_1 = User.objects.create_user(
            username="customer_user_1", email="customer_user_1@example.com", password="x"
        )
        Profile.objects.create(user=cls.customer_user_1, type="customer")

        cls.customer_user_2 = User.objects.create_user(
            username="customer_user_2", email="customer_user_2@example.com", password="x"
        )
        Profile.objects.create(user=cls.customer_user_2, type="customer")

        cls.review_1 = Review.objects.create(
            business_user=cls.business_user_1,
            reviewer=cls.customer_user_1,
            rating=5,
            description="Great service!"
        )

        cls.list_url = reverse("review-list")
        cls.detail_1_url = reverse("review-detail", args=[cls.review_1.id])
    
    def test_post_401_unauthenticated(self):
        data = {
            "business_user": self.business_user_2.id,
            "rating": 4,
            "description": "Good job!"
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_403_not_customer(self):
        self.client.force_authenticate(self.business_user_1)
        data = {
            "business_user": self.business_user_2.id,
            "rating": 4,
            "description": "Good job!"
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_401_unauthenticated(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_401_unauthenticated(self):
        data = {
            "rating": 4,
            "description": "Good job!"
        }
        resp = self.client.patch(self.detail_1_url, data)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_403_not_author(self):
        self.client.force_authenticate(self.customer_user_2)
        data = {
            "rating": 4,
            "description": "Good job!"
        }
        resp = self.client.patch(self.detail_1_url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_401_unauthenticated(self):
        resp = self.client.delete(self.detail_1_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_403_not_author(self):
        self.client.force_authenticate(self.customer_user_2)
        resp = self.client.delete(self.detail_1_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)