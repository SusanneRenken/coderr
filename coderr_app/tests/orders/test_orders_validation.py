from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail


class OrderPermissionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.business_user = User.objects.create_user(
            username="business_user", email="business_user@example.com", password="x"
        )
        Profile.objects.create(user=cls.business_user, type="business")

        cls.customer_user = User.objects.create_user(
            username="customer_user", email="customer_user@example.com", password="x"
        )
        Profile.objects.create(user=cls.customer_user, type="customer")

        cls.offer = Offer.objects.create(
            user=cls.business_user, title="First test Offer", description="For tests"
        )
        cls.offer_detail_basic = OfferDetail.objects.create(
            offer=cls.offer, title="Basic", revisions=1,
            delivery_time_in_days=3, price=50, features=["A"], offer_type="basic"
        )
        cls.offer_detail_standard = OfferDetail.objects.create(
            offer=cls.offer, title="Standard", revisions=2,
            delivery_time_in_days=5, price=100, features=["A", "B"], offer_type="standard"
        )
        cls.offer_detail_premium = OfferDetail.objects.create(
            offer=cls.offer, title="Premium", revisions=3,
            delivery_time_in_days=7, price=200, features=["A", "B", "C"], offer_type="premium"
        )

        cls.list_url = reverse("order-list")

    def test_post_400_empty_data(self):
        self.client.force_authenticate(self.customer_user)
        data = {}
        resp = self.client.post(self.list_url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_400_invalid_data(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "offer_detail_id": "invalid"
        }
        resp = self.client.post(self.list_url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_404_offer_detail_not_found(self):
        self.client.force_authenticate(self.customer_user)
        data = {
            "offer_detail_id": 9999
        }
        resp = self.client.post(self.list_url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)