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

        cls.customer_user = User.objects.create_user(
            username="customer_user_1", email="customer_user_1@example.com", password="x"
        )
        Profile.objects.create(user=cls.customer_user, type="customer")

        cls.review_1 = Review.objects.create(
            business_user=cls.business_user_1,
            reviewer=cls.customer_user,
            rating=5,
            description="Great service!"
        )

        cls.list_url = reverse("review-list")
        cls.detail_url = reverse("review-detail", args=[cls.review_1.id])

    def test_post_400_invalid_rating(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "business_user": self.business_user_2.id,
            "rating": 6,
            "description": "Good job!"
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', resp.data)
    
    def test_post_400_missing_business_user(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "rating": 4,
            "description": "Greate!"
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('business_user', resp.data)

    def test_post_400_missing_rating(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "business_user": self.business_user_2.id,
            "description": "Greate!"
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', resp.data)
    
    def test_post_400_missing_description(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "business_user": self.business_user_2.id,
            "rating": 4
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', resp.data)

    def test_post_400_second_review_same_business_user(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "business_user": self.business_user_1.id,
            "rating": 4,
            "description": "Super!"
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)

    def test_patch_400_invalid_rating(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "rating": 0,
            "description": "Updated review"
        }
        resp = self.client.patch(self.detail_url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', resp.data)

    def test_patch_400_forbidden_field_business_user(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "business_user": self.business_user_2.id,
            "rating": 4,
            "description": "Updated review"
        }
        resp = self.client.patch(self.detail_url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)

    def test_patch_400_forbidden_field_reviewer(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "reviewer": self.customer_user.id,
            "rating": 4,
            "description": "Updated review"
        }
        resp = self.client.patch(self.detail_url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)

    def test_patch_404_nonexistent_review(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "rating": 4,
            "description": "Updated review"
        }
        url = reverse("review-detail", args=[999])
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_404_nonexistent_review(self):
        self.client.force_authenticate(self.customer_user)
        url = reverse("review-detail", args=[999])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)