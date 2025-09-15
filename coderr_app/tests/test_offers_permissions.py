from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail


class OfferPermissionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Users
        cls.business_user = User.objects.create_user(
            username="business_user", email="business_user@example.com", password="x"
        )
        Profile.objects.create(user=cls.business_user, type="business")

        cls.customer_user = User.objects.create_user(
            username="customer_user", email="customer_user@example.com", password="x"
        )
        Profile.objects.create(user=cls.customer_user, type="customer")

        # Offer for Detail-GET-Tests
        cls.offer = Offer.objects.create(
            user=cls.business_user, title="First test Offer", description="For tests"
        )
        OfferDetail.objects.create(
            offer=cls.offer, title="Basic", revisions=1,
            delivery_time_in_days=3, price=50, features=["A"], offer_type="basic"
        )
        OfferDetail.objects.create(
            offer=cls.offer, title="Standard", revisions=2,
            delivery_time_in_days=5, price=100, features=["A", "B"], offer_type="standard"
        )
        OfferDetail.objects.create(
            offer=cls.offer, title="Premium", revisions=3,
            delivery_time_in_days=7, price=200, features=["A", "B", "C"], offer_type="premium"
        )

        # URLs
        cls.list_url = reverse("offer-list")
        cls.detail_url = reverse("offer-detail", args=[cls.offer.id])

    def _payload(self):
        return {
            "title": "T",
            "description": "D",
            "details": [
                {"title": "Basic",    "revisions": 1, "delivery_time_in_days": 3,
                 "price": 50,  "features": ["A"],        "offer_type": "basic"},
                {"title": "Standard", "revisions": 2, "delivery_time_in_days": 5,
                 "price": 100, "features": ["A", "B"],    "offer_type": "standard"},
                {"title": "Premium",  "revisions": 3, "delivery_time_in_days": 7,
                 "price": 200, "features": ["A", "B", "C"], "offer_type": "premium"},
            ],
        }

    # --- POST Permissions ---

    def test_post_401_anonymous(self):
        resp = self.client.post(self.list_url, self._payload(), format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Offer.objects.count(), 1)

    def test_post_403_non_business_user(self):
        self.client.force_authenticate(user=self.customer_user)
        resp = self.client.post(self.list_url, self._payload(), format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Offer.objects.count(), 1)

    # --- GET Permissions ---

    def test_get_401_offer_detail_requires_auth(self):
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- PATCH Permissions ---

    def test_patch_401_offer_detail_requires_auth(self):
        resp = self.client.patch(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_403_non_business_user(self):
        self.client.force_authenticate(user=self.customer_user)
        resp = self.client.patch(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
