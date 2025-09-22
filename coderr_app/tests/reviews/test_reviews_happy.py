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

        cls.review_2 = Review.objects.create(
            business_user=cls.business_user_1,
            reviewer=cls.customer_user_2,
            rating=4,
            description="Good service!"
        )

        cls.review_3 = Review.objects.create(
            business_user=cls.business_user_2,
            reviewer=cls.customer_user_2,
            rating=3,
            description="Average service!"
        )

        cls.list_url = reverse("review-list")
        cls.detail_1_url = reverse("review-detail", args=[cls.review_1.id])

    def test_post_201_review(self):
        self.client.force_authenticate(self.customer_user_1)
        data = {
            "business_user": self.business_user_2.id,
            "rating": 4,
            "description": "Good job!"
        }
        resp = self.client.post(self.list_url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['business_user'], self.business_user_2.id)
        self.assertEqual(resp.data['reviewer'], self.customer_user_1.id)
        self.assertEqual(resp.data['rating'], 4)
        self.assertEqual(resp.data['description'], "Good job!")

    def test_get_200_reviews_list(self):
        self.client.force_authenticate(self.customer_user_1)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 3)

    def test_get_200_revies_business_user_filter(self):
        self.client.force_authenticate(self.customer_user_1)
        resp = self.client.get(self.list_url, {'business_user_id': self.business_user_1.id})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        for review in resp.data:
            self.assertEqual(review['business_user'], self.business_user_1.id)

    def test_get_200_revies_reviewer_filter(self):
        self.client.force_authenticate(self.customer_user_1)
        resp = self.client.get(self.list_url, {'reviewer_id': self.customer_user_2.id})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        for review in resp.data:
            self.assertEqual(review['reviewer'], self.customer_user_2.id)

    def test_patch_200_review(self):
        self.client.force_authenticate(self.customer_user_1)
        data = {
            "rating": 4,
            "description": "Good job!"
        }
        resp = self.client.patch(self.detail_1_url, data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['business_user'], self.business_user_1.id)
        self.assertEqual(resp.data['reviewer'], self.customer_user_1.id)
        self.assertEqual(resp.data['rating'], 4)
        self.assertEqual(resp.data['description'], "Good job!")
    
    def test_delete_204_review(self):
        self.client.force_authenticate(self.customer_user_1)
        resp = self.client.delete(self.detail_1_url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        resp = self.client.get(self.detail_1_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

