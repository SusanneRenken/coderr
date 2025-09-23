from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail, Order, Review


class OrderHappyTests(APITestCase):

    @classmethod
    def setUpTestData(cls):

        # Create business users
        cls.business_user_1 = User.objects.create_user(
            username="business_user_1", email="business_user_1@example.com", password="x"
        )
        Profile.objects.create(user=cls.business_user_1, type="business")

        cls.business_user_2 = User.objects.create_user(
            username="business_user_2", email="business_user_2@example.com", password="x"
        )
        Profile.objects.create(user=cls.business_user_2, type="business")


        # Create customer users
        cls.customer_user_1 = User.objects.create_user(
            username="customer_user_1", email="customer_user_1@example.com", password="x"
        )
        Profile.objects.create(user=cls.customer_user_1, type="customer")


        cls.customer_user_2 = User.objects.create_user(
            username="customer_user_2", email="customer_user_2@example.com", password="x"
        )
        Profile.objects.create(user=cls.customer_user_2, type="customer")


        # Create offers with offer details
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

        # Create reviews
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

    def test_get_200_baseinfo(self):
        url = reverse("base-info")
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['review_count'], 3)
        self.assertEqual(resp.data['average_rating'], 4.0)
        self.assertEqual(resp.data['business_profile_count'], 2)
        self.assertEqual(resp.data['offer_count'], 2)
