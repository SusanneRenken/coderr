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
    
    # --- POST Happy Offer ---

    def test_post_201_offer(self):
        self.client.force_authenticate(user=self.business_user)
        offernum_before = Offer.objects.count()
        detailnum_before = OfferDetail.objects.count()
        response = self.client.post(
            self.list_url, self._payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check main offer fields
        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], self._payload()['title'])
        self.assertEqual(response.data['description'],
                         self._payload()['description'])
        self.assertIn('details', response.data)

        # Check details
        details = response.data['details']
        self.assertEqual(len(details), 3)
        types = {d['offer_type'] for d in details}
        self.assertSetEqual(types, {'basic', 'standard', 'premium'})
        for d in details:
            for key in ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']:
                self.assertIn(key, d)
            self.assertIsInstance(d['features'], list)

        # Check DB state
        self.assertEqual(Offer.objects.count(), offernum_before + 1)
        self.assertEqual(OfferDetail.objects.count(), detailnum_before + 3)

    def test_post_201_offer_with_image_null(self):
        self.client.force_authenticate(user=self.business_user)
        response = self.client.post(
            self.list_url, self._payload(), format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', response.data)
        self.assertIsNone(response.data['image'])

    def test_patch_201_200_image_after_post(self):
        self.client.force_authenticate(user=self.business_user)

        # Create offer without image
        create_resp = self.client.post(
            self.list_url, self._payload(), format='json')

        # Check creation worked
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 2)
        offer_id = create_resp.data['id']
        self.assertIsNone(create_resp.data['image'])

        # Patch image
        file_bytes = b'fake image bytes'
        upload = SimpleUploadedFile(
            'logo.png', file_bytes, content_type='image/png')
        patch_resp = self.client.patch(
            reverse('offer-detail', args=[offer_id]),
            data={'image': upload},
            format='multipart'
)

        # Check patch worked
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertIn('image', patch_resp.data)
        self.assertIsNotNone(patch_resp.data['image'])
        self.assertIn('/media/offers/', patch_resp.data['image'])
        self.assertTrue(patch_resp.data['image'].endswith('.png'))

    # --- GET Happy Offer ---

    def test_get_200_offers_list_returns_paginated_envelope(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for key in ["count", "next", "previous", "results"]:
            self.assertIn(key, resp.data)
        self.assertLessEqual(len(resp.data["results"]), 6)

    def test_get_200_offers_list_item_shape(self):
        resp = self.client.get(self.list_url)
        item = resp.data["results"][0]
        expected_keys = {
            "id", "user", "title", "image", "description",
            "created_at", "updated_at", "details",
            "min_price", "min_delivery_time", "user_detail"
        }
        self.assertTrue(expected_keys.issubset(item.keys()))

    def test_get_200_offers_list_details_are_links_only(self):
        resp = self.client.get(self.list_url)
        details = resp.data["results"][0]["details"]
        self.assertEqual(len(details), 3)
        for d in details:
            self.assertEqual(set(d.keys()), {"id", "url"})
            self.assertIn("/api/offerdetails/", d["url"])

    def test_get_200_offers_list_min_price_and_delivery_time(self):
        resp = self.client.get(self.list_url)
        item = resp.data["results"][0]
        self.assertEqual(item["min_price"], 50)
        self.assertEqual(item["min_delivery_time"], 3)

    

    def test_get_200_offer_detail_item_shape(self):
        self.client.force_authenticate(user=self.business_user)
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for key in ["id", "user", "title", "image", "description",
                    "created_at", "updated_at", "details",
                    "min_price", "min_delivery_time"]:
            self.assertIn(key, resp.data)
        self.assertNotIn("user_detail", resp.data)

    def test_get_200_offer_detail_details_are_links_only(self):
        self.client.force_authenticate(user=self.business_user)
        resp = self.client.get(self.detail_url)
        details = resp.data["details"]
        for d in details:
            self.assertEqual(set(d.keys()), {"id", "url"})
            self.assertIn("/api/offerdetails/", d["url"])

    def test_get_200_offers_detail_min_price_and_delivery_time(self):
        self.client.force_authenticate(user=self.business_user)
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["min_price"], 50)
        self.assertEqual(resp.data["min_delivery_time"], 3)
