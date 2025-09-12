from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Offer

class OfferPermissionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.biz_user = User.objects.create_user(
            username="biz", email="biz@example.com", password="x"
        )
        Profile.objects.create(user=cls.biz_user, type="business")

        cls.cust_user = User.objects.create_user(
            username="cust", email="cust@example.com", password="x"
        )
        Profile.objects.create(user=cls.cust_user, type="customer")

        cls.url = reverse("offer-list")

    def _payload(self):
        return {
            "title": "T",
            "description": "D",
            "details": [
                {"title": "Basic",    "revisions": 1, "delivery_time_in_days": 3,
                    "price": 50,  "features": ["A"],       "offer_type": "basic"},
                {"title": "Standard", "revisions": 2, "delivery_time_in_days": 5,
                    "price": 100, "features": ["A", "B"],    "offer_type": "standard"},
                {"title": "Premium",  "revisions": 3, "delivery_time_in_days": 7,
                    "price": 200, "features": ["A", "B", "C"], "offer_type": "premium"},
            ],
        }

    def test_post_401_anonymous(self):
        resp = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Offer.objects.count(), 0)

    def test_post_403_non_business_user(self):
        self.client.force_authenticate(user=self.cust_user)
        resp = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), 0)

    def test_post_201_business_user(self):
        self.client.force_authenticate(user=self.biz_user)
        resp = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 1)

    def test_list_is_public_even_with_global_IsAuthenticated(self):
        url = reverse("offer-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_list_authenticated_ok(self):
        self.client.force_authenticate(user=self.biz_user)
        url = reverse("offer-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

