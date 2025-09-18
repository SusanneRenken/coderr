from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail


class OfferHappyTests(APITestCase):
    
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

        def test_post_201_order(self):
            self.client.force_authenticate(self.customer_user)
            data = {
                "offer_detail": self.offer_detail_basic.id
            }
            resp = self.client.post(self.list_url, data, format='json')

            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
            self.assertEqual(resp.data['customer_user'], self.customer_user.id)
            self.assertEqual(resp.data['business_user'], self.business_user.id)
            self.assertEqual(resp.data['status'], 'in_progress')
            self.assertEqual(resp.data['title'], self.offer_detail_basic.title)
            self.assertEqual(resp.data['revisions'], self.offer_detail_basic.revisions)
            self.assertEqual(resp.data['delivery_time_in_days'], self.offer_detail_basic.delivery_time_in_days)
            self.assertEqual(resp.data['price'], self.offer_detail_basic.price)
            self.assertEqual(resp.data['features'], self.offer_detail_basic.features)
            self.assertEqual(resp.data['offer_type'], self.offer_detail_basic.offer_type)