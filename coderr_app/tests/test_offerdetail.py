from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail


class OffersHappyTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="business_user", email="business_user@example.com", password="x"
        )
        Profile.objects.create(user=cls.user, type="business")


        cls.offer = Offer.objects.create(
            user=cls.user, title="First test Offer", description="For tests"
        )
        cls.offerdetail_1 =OfferDetail.objects.create(
            offer=cls.offer, title="Basic", revisions=1,
            delivery_time_in_days=3, price=50, features=["A"], offer_type="basic"
        )
        cls.offerdetail_2 = OfferDetail.objects.create(
            offer=cls.offer, title="Standard", revisions=2,
            delivery_time_in_days=5, price=100, features=["A", "B"], offer_type="standard"
        )
        cls.offerdetail_3 = OfferDetail.objects.create(
            offer=cls.offer, title="Premium", revisions=3,
            delivery_time_in_days=7, price=200, features=["A", "B", "C"], offer_type="premium"
        )

        cls.url_detail_1 = reverse("offerdetail-detail", args=[cls.offerdetail_1.id])
        cls.url_detail_2 = reverse("offerdetail-detail", args=[cls.offerdetail_2.id])
        cls.url_detail_3 = reverse("offerdetail-detail", args=[cls.offerdetail_3.id])

    def test_get_200_offerdetail(self):
        self.client.force_authenticate(self.user)
        resp = self.client.get(self.url_detail_1)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['id'], self.offerdetail_1.id)
        self.assertEqual(resp.data['title'], "Basic")
        self.assertEqual(resp.data['revisions'], 1)
        self.assertEqual(resp.data['delivery_time_in_days'], 3)
        self.assertEqual(resp.data['price'], 50)
        self.assertEqual(resp.data['features'], ["A"])
        self.assertEqual(resp.data['offer_type'], "basic")

    def test_get_401_offerdetail(self):
        resp = self.client.get(self.url_detail_1)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_404_offerdetail(self):
        self.client.force_authenticate(self.user)
        url = reverse("offerdetail-detail", args=[999])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)