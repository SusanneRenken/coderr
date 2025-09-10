from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from copy import deepcopy
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail
import json

class OffersHappyPathTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        cls.user_profile = Profile.objects.create(user=cls.user, type='business')
    
    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_create_offer(self):
        url =  reverse('offer-list')
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
                {"title": "Basic", "revisions": 1, "delivery_time_in_days": 3, "price": 50,  "features": ["A"],       "offer_type": "basic"},
                {"title": "Standard", "revisions": 2, "delivery_time_in_days": 5, "price": 100, "features": ["A","B"],    "offer_type": "standard"},
                {"title": "Premium",  "revisions": 3, "delivery_time_in_days": 7, "price": 200, "features": ["A","B","C"],"offer_type": "premium"},
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
                {"title": "Basic", "revisions": 1, "delivery_time_in_days": 3, "price": 50,  "features": ["A"],       "offer_type": "basic"},
                {"title": "Standard", "revisions": 2, "delivery_time_in_days": 5, "price": 100, "features": ["A","B"],    "offer_type": "standard"},
                {"title": "Premium",  "revisions": 3, "delivery_time_in_days": 7, "price": 200, "features": ["A","B","C"],"offer_type": "premium"},
            ]
        }
        create_resp = self.client.post(create_url, payload, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        offer_id = create_resp.data['id']
        self.assertIsNone(create_resp.data['image'])

        detail_url = reverse('offer-detail', args=[offer_id])
        file_bytes = b'fake image bytes'
        upload = SimpleUploadedFile('logo.png', file_bytes, content_type='image/png')
        patch_resp = self.client.patch(detail_url, data={'image': upload}, format='multipart')
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertIn('image', patch_resp.data)
        self.assertIsNotNone(patch_resp.data['image'])
        self.assertIn('logo.png', patch_resp.data['image'])

    

class OfferValidationTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="biz", email="biz@example.com", password="x"
        )
        Profile.objects.create(user=cls.user, type="business")

    def setUp(self):
        self.client.force_authenticate(self.user)
        self.url = reverse("offer-list")

    def _base_details(self):
        return [
            {"title": "Basic", "revisions": 1, "delivery_time_in_days": 3, "price": 50,  "features": ["A"], "offer_type": "basic"},
            {"title": "Standard", "revisions": 2, "delivery_time_in_days": 5, "price": 100, "features": ["A","B"], "offer_type": "standard"},
            {"title": "Premium", "revisions": 3, "delivery_time_in_days": 7, "price": 200, "features": ["A","B","C"], "offer_type": "premium"},
        ]

    def _payload(self, details=None, **overrides):
        data = {
            "title": "T",
            "description": "D",
            "details": details if details is not None else self._base_details(),
        }
        data.update(overrides)
        return data

    def _post(self, data):
        return self.client.post(self.url, data, format="json")

    def test_400_missing_details(self):
        data = self._payload()
        data.pop("details")
        resp = self._post(data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_400_not_three_details(self):
        cases = [
            self._base_details()[:2],
            self._base_details() + [deepcopy(self._base_details()[0])],
        ]
        for details in cases:
            with self.subTest(len=len(details)):
                resp = self._post(self._payload(details=details))
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_400_duplicate_or_missing_types(self):
        base = self._base_details()
        cases = [
            [
                {**base[0], "offer_type": "basic"},
                {**base[1], "offer_type": "basic"},
                {**base[2], "offer_type": "standard"},
            ],
            [
                {**base[0], "offer_type": "gold"},
                {**base[1], "offer_type": "standard"},
                {**base[2], "offer_type": "premium"},
            ],
        ]
        for details in cases:
            with self.subTest(details=[d["offer_type"] for d in details]):
                resp = self._post(self._payload(details=details))
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_400_invalid_field_values(self):
        base = self._base_details()
        bad_cases = [
            {**base[0], "revisions": -1},
            {**base[0], "delivery_time_in_days": 0},
            {**base[0], "price": -5},
            {**base[0], "features": "not-a-list"},
        ]
        for bad in bad_cases:
            with self.subTest(bad=bad):
                details = [bad, base[1], base[2]]
                resp = self._post(self._payload(details=details))
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


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
                {"title": "Basic",    "revisions": 1, "delivery_time_in_days": 3, "price": 50,  "features": ["A"],       "offer_type": "basic"},
                {"title": "Standard", "revisions": 2, "delivery_time_in_days": 5, "price": 100, "features": ["A","B"],    "offer_type": "standard"},
                {"title": "Premium",  "revisions": 3, "delivery_time_in_days": 7, "price": 200, "features": ["A","B","C"],"offer_type": "premium"},
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