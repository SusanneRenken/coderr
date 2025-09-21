from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail, Order


class OrderPermissionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):

        # Create two business users with offers
        cls.business_user_1 = User.objects.create_user(
            username="business_user_1", email="business_user_1@example.com", password="x"
        )
        Profile.objects.create(user=cls.business_user_1, type="business")

        cls.offer_1 = Offer.objects.create(
            user=cls.business_user_1, title="Offer from Business User 1", description="For tests for business user 1"
        )
        cls.offer_detail_basic_1 = OfferDetail.objects.create(
            offer=cls.offer_1, title="Basic form Offer 1", revisions=1,
            delivery_time_in_days=3, price=50, features=["A"], offer_type="basic"
        )
        cls.offer_detail_standard_1 = OfferDetail.objects.create(
            offer=cls.offer_1, title="Standard form Offer 1", revisions=2,
            delivery_time_in_days=5, price=100, features=["A", "B"], offer_type="standard"
        )
        cls.offer_detail_premium_1 = OfferDetail.objects.create(
            offer=cls.offer_1, title="Premium form Offer 1", revisions=3,
            delivery_time_in_days=7, price=200, features=["A", "B", "C"], offer_type="premium"
        )

        cls.business_user_2 = User.objects.create_user(
            username="business_user_2", email="business_user_2@example.com", password="x"
        )
        Profile.objects.create(user=cls.business_user_2, type="business")

        cls.offer_2 = Offer.objects.create(
            user=cls.business_user_2, title="Offer from Business User 2", description="For tests for business user 2"
        )
        cls.offer_detail_basic_2 = OfferDetail.objects.create(
            offer=cls.offer_2, title="Basic form Offer 2", revisions=1,
            delivery_time_in_days=3, price=50, features=["A"], offer_type="basic"
        )
        cls.offer_detail_standard_2 = OfferDetail.objects.create(
            offer=cls.offer_2, title="Standard form Offer 2", revisions=2,
            delivery_time_in_days=5, price=100, features=["A", "B"], offer_type="standard"
        )
        cls.offer_detail_premium_2 = OfferDetail.objects.create(
            offer=cls.offer_2, title="Premium form Offer 2", revisions=3,
            delivery_time_in_days=7, price=200, features=["A", "B", "C"], offer_type="premium"
        )

        # Create two customer users with orders
        cls.customer_user_1 = User.objects.create_user(
            username="customer_user_1", email="customer_user_1@example.com", password="x"
        )
        Profile.objects.create(user=cls.customer_user_1, type="customer")

        cls.order_11_1 = Order.objects.create(
            customer_user=cls.customer_user_1,
            offer_detail=cls.offer_detail_basic_1,
            business_user=cls.offer_detail_basic_1.offer.user,
        )

        cls.order_12 = Order.objects.create(
            customer_user=cls.customer_user_1,
            offer_detail=cls.offer_detail_standard_2,
            business_user=cls.offer_detail_standard_2.offer.user,
        )

        cls.order_12_2 = Order.objects.create(
            customer_user=cls.customer_user_1,
            offer_detail=cls.offer_detail_basic_2,
            business_user=cls.offer_detail_basic_2.offer.user,
        )

        cls.customer_user_2 = User.objects.create_user(
            username="customer_user_2", email="customer_user_2@example.com", password="x"
        )
        Profile.objects.create(user=cls.customer_user_2, type="customer")

        cls.order_21 = Order.objects.create(
            customer_user=cls.customer_user_2,
            offer_detail=cls.offer_detail_premium_1,
            business_user=cls.offer_detail_premium_1.offer.user,
        )

        cls.order_22 = Order.objects.create(
            customer_user=cls.customer_user_2,
            offer_detail=cls.offer_detail_basic_2,
            business_user=cls.offer_detail_basic_2.offer.user,
        )

        cls.list_url = reverse("order-list")

    def test_post_400_empty_data(self):
        self.client.force_authenticate(self.customer_user_1)
        data = {}
        resp = self.client.post(self.list_url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_400_invalid_data(self):
        self.client.force_authenticate(self.customer_user_1)
        data = {
            "offer_detail_id": "invalid"
        }
        resp = self.client.post(self.list_url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_404_offer_detail_not_found(self):
        self.client.force_authenticate(self.customer_user_1)
        data = {
            "offer_detail_id": 9999
        }
        resp = self.client.post(self.list_url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_400_invalid_status(self):
        self.client.force_authenticate(self.business_user_1)
        url = reverse("order-detail", args=[self.order_11_1.id])
        data = {
            "status": "invalid_status"
        }
        resp = self.client.patch(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_400_empty_data(self):
        self.client.force_authenticate(self.business_user_1)
        url = reverse("order-detail", args=[self.order_11_1.id])
        data = {}
        resp = self.client.patch(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_400_forbidden_fields(self):
        self.client.force_authenticate(self.business_user_1)
        url = reverse("order-detail", args=[self.order_11_1.id])
        data = {
            "offer_detail_id": 1
        }
        resp = self.client.patch(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_404_order_not_found(self):
        self.client.force_authenticate(self.business_user_1)
        url = reverse("order-detail", args=[9999])
        data = {
            "status": "completed"
        }
        resp = self.client.patch(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_404_order_count_no_business_user(self):
        self.client.force_authenticate(self.customer_user_1)
        url = reverse("order-count", args=[9999])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_404_completed_order_count_no_business_user(self):
        self.client.force_authenticate(self.customer_user_1)
        url = reverse("completed-order-count", args=[9999])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
