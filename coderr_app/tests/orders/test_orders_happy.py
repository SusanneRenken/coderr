from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail, Order


class OrderHappyTests(APITestCase):

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

    def test_post_201_order(self):
        self.client.force_authenticate(self.customer_user_1)
        data = {
            "offer_detail_id": self.offer_detail_basic_1.id
        }
        resp = self.client.post(self.list_url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['customer_user'], self.customer_user_1.id)
        self.assertEqual(resp.data['business_user'], self.business_user_1.id)
        self.assertEqual(resp.data['status'], 'in_progress')
        self.assertEqual(resp.data['title'], self.offer_detail_basic_1.title)
        self.assertEqual(resp.data['revisions'],
                         self.offer_detail_basic_1.revisions)
        self.assertEqual(resp.data['delivery_time_in_days'],
                         self.offer_detail_basic_1.delivery_time_in_days)
        self.assertEqual(resp.data['price'], self.offer_detail_basic_1.price)
        self.assertEqual(resp.data['features'],
                         self.offer_detail_basic_1.features)
        self.assertEqual(resp.data['offer_type'],
                         self.offer_detail_basic_1.offer_type)

    def test_get_200_order_list_customer(self):
        self.client.force_authenticate(self.customer_user_1)

        resp = self.client.get(self.list_url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 3)

    def test_get_200_order_list_business(self):
        self.client.force_authenticate(self.business_user_1)

        resp = self.client.get(self.list_url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)

    def test_patch_200_order_status(self):
        self.client.force_authenticate(self.business_user_1)
        url = reverse("order-detail", args=[self.order_11_1.id])
        data = {
            "status": "completed"
        }
        resp = self.client.patch(url, data, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['status'], 'completed')

    def test_delete_204_order(self):
        staff_user = User.objects.create_user(
            username="admin", email="admin@example.com", password="x", is_staff=True
        )
        self.client.force_authenticate(staff_user)
        url = reverse("order-detail", args=[self.order_11_1.id])
        resp = self.client.delete(url)

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order_11_1.id).exists())

    def test_get_200_order_count(self):
        self.client.force_authenticate(self.business_user_1)
        url = reverse("order-count", args=[self.business_user_1.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['order_count'], 2)

    def test_get_200_completed_order_count(self):
        self.client.force_authenticate(self.business_user_1)
        url = reverse("completed-order-count", args=[self.business_user_1.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['completed_order_count'], 0)
