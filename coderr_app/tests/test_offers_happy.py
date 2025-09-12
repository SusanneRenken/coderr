from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail


class OffersPostPatchTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        cls.user_profile = Profile.objects.create(
            user=cls.user, type='business')

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_create_offer(self):
        url = reverse('offer-list')
        data = {
            "title": "Test Offer",
            "description": "This is a test offer",
            "details": [
                {
                    "title": "Basic Package",
                    "revisions": 1,
                    "delivery_time_in_days": 3,
                    "price": 50,
                    "features": ["Feature A", "Feature B"],
                    "offer_type": "basic"
                },
                {
                    "title": "Standard Package",
                    "revisions": 2,
                    "delivery_time_in_days": 5,
                    "price": 100,
                    "features": ["Feature A", "Feature B", "Feature C"],
                    "offer_type": "standard"
                },
                {
                    "title": "Premium Package",
                    "revisions": 3,
                    "delivery_time_in_days": 7,
                    "price": 200,
                    "features": ["Feature A", "Feature B", "Feature C", "Feature D"],
                    "offer_type": "premium"
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertIn('id', response.data)
        self.assertEqual(response.data['title'], data['title'])
        self.assertEqual(response.data['description'], data['description'])
        self.assertIn('details', response.data)

        details = response.data['details']
        self.assertEqual(len(details), 3)

        types = {d['offer_type'] for d in details}
        self.assertSetEqual(types, {'basic', 'standard', 'premium'})

        for d in details:
            for key in ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']:
                self.assertIn(key, d)
            self.assertIsInstance(d['features'], list)

        self.assertEqual(Offer.objects.count(), 1)
        self.assertEqual(OfferDetail.objects.count(), 3)

        offer = Offer.objects.first()
        self.assertEqual(offer.user, self.user)
        self.assertEqual(offer.details.count(), 3)

    def test_post_creates_offer_with_image_null(self):
        """POST (JSON) legt das Offer an und image ist null."""
        url = reverse('offer-list')
        payload = {
            "title": "Offer ohne Bild",
            "description": "Nur Daten, kein File",
            "details": [
                {"title": "Basic", "revisions": 1, "delivery_time_in_days": 3,
                    "price": 50,  "features": ["A"],       "offer_type": "basic"},
                {"title": "Standard", "revisions": 2, "delivery_time_in_days": 5,
                    "price": 100, "features": ["A", "B"],    "offer_type": "standard"},
                {"title": "Premium",  "revisions": 3, "delivery_time_in_days": 7,
                    "price": 200, "features": ["A", "B", "C"], "offer_type": "premium"},
            ]
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', resp.data)
        self.assertIsNone(resp.data['image'])

    def test_patch_image_after_post(self):
        """Nach dem POST wird das Bild per PATCH (multipart) gesetzt."""
        create_url = reverse('offer-list')
        payload = {
            "title": "Offer mit anschließendem Bild",
            "description": "Wird gleich gepatcht",
            "details": [
                {"title": "Basic", "revisions": 1, "delivery_time_in_days": 3,
                    "price": 50,  "features": ["A"],       "offer_type": "basic"},
                {"title": "Standard", "revisions": 2, "delivery_time_in_days": 5,
                    "price": 100, "features": ["A", "B"],    "offer_type": "standard"},
                {"title": "Premium",  "revisions": 3, "delivery_time_in_days": 7,
                    "price": 200, "features": ["A", "B", "C"], "offer_type": "premium"},
            ]
        }
        create_resp = self.client.post(create_url, payload, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        offer_id = create_resp.data['id']
        self.assertIsNone(create_resp.data['image'])

        detail_url = reverse('offer-detail', args=[offer_id])
        file_bytes = b'fake image bytes'
        upload = SimpleUploadedFile(
            'logo.png', file_bytes, content_type='image/png')
        patch_resp = self.client.patch(
            detail_url, data={'image': upload}, format='multipart')
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertIn('image', patch_resp.data)
        self.assertIsNotNone(patch_resp.data['image'])
        self.assertIn('/media/offers/', patch_resp.data['image'])
        self.assertTrue(patch_resp.data['image'].endswith('.png'))


class OffersGetTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="listuser",
            email="listuser@example.com",
            password="testpassword"
        )
        Profile.objects.create(user=cls.user, type="business")

        cls.offer = Offer.objects.create(
            user=cls.user,
            title="Listen-Offer",
            description="Offer für GET Tests"
        )
        OfferDetail.objects.create(
            offer=cls.offer, title="Basic", revisions=1,
            delivery_time_in_days=3, price=50,
            features=["A"], offer_type="basic"
        )
        OfferDetail.objects.create(
            offer=cls.offer, title="Standard", revisions=2,
            delivery_time_in_days=5, price=100,
            features=["A", "B"], offer_type="standard"
        )
        OfferDetail.objects.create(
            offer=cls.offer, title="Premium", revisions=3,
            delivery_time_in_days=7, price=200,
            features=["A", "B", "C"], offer_type="premium"
        )

    def test_get_offers_list_returns_paginated_envelope(self):
        url = reverse("offer-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for key in ["count", "next", "previous", "results"]:
            self.assertIn(key, resp.data)

    def test_get_offers_list_item_shape(self):
        url = reverse("offer-list")
        resp = self.client.get(url)
        item = resp.data["results"][0]
        expected_keys = {
            "id", "user", "title", "image", "description",
            "created_at", "updated_at", "details",
            "min_price", "min_delivery_time", "user_detail"
        }
        self.assertTrue(expected_keys.issubset(item.keys()))

    def test_get_offers_list_details_are_links_only(self):
        url = reverse("offer-list")
        resp = self.client.get(url)
        details = resp.data["results"][0]["details"]
        self.assertEqual(len(details), 3)
        for d in details:
            self.assertEqual(set(d.keys()), {"id", "url"})
            self.assertIn("/api/offerdetails/", d["url"])

    def test_get_offers_list_min_price_and_delivery_time(self):
        url = reverse("offer-list")
        resp = self.client.get(url)
        item = resp.data["results"][0]
        self.assertEqual(item["min_price"], 50)
        self.assertEqual(item["min_delivery_time"], 3)

