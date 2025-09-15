from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from copy import deepcopy
from auth_app.models import Profile


class OfferValidationTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="business_user", email="business_user@example.com", password="x"
        )
        Profile.objects.create(user=cls.user, type="business")
        cls.list_url = reverse("offer-list")

    def setUp(self):
        self.client.force_authenticate(self.user)

    def _base_details(self):
        return [
            {"title": "Basic", "revisions": 1, "delivery_time_in_days": 3,
             "price": 50,  "features": ["A"], "offer_type": "basic"},
            {"title": "Standard", "revisions": 2, "delivery_time_in_days": 5,
             "price": 100, "features": ["A", "B"], "offer_type": "standard"},
            {"title": "Premium", "revisions": 3, "delivery_time_in_days": 7,
             "price": 200, "features": ["A", "B", "C"], "offer_type": "premium"},
        ]

    def _payload(self, details=None, **overrides):
        data = {
            "title": "T",
            "description": "D",
            "details": details if details is not None else self._base_details(),
        }
        data.update(overrides)
        return data
    
    # --- POST Validations ---

    def test_post_400_missing_details(self):
        data = self._payload()
        data.pop("details")
        resp = self.client.post(self.list_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_400_not_three_details(self):
        cases = [
            self._base_details()[:2],
            self._base_details() + [deepcopy(self._base_details()[0])],
        ]
        for details in cases:
            with self.subTest(len=len(details)):
                resp = self.client.post(
                    self.list_url, self._payload(details=details), format="json"
                )
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_400_duplicate_or_missing_types(self):
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
                resp = self.client.post(
                    self.list_url, self._payload(details=details), format="json"
                )
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_400_invalid_field_values(self):
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
                resp = self.client.post(
                    self.list_url, self._payload(details=details), format="json"
                )
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # --- GET Validations ---

    def test_get_404_out_of_range_page_returns(self):
        self.client.post(self.list_url, self._payload(), format="json")
        resp = self.client.get(self.list_url + "?page=999")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_404_no_offer_with_this_id(self):
        resp = self.client.get(reverse("offer-detail", args=[999]))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # --- PATCH Validations ---

    def test_patch_400_duplicate_types_in_details(self):
        # Create an offer first
        post_resp = self.client.post(self.list_url, self._payload(), format="json")
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        offer_id = post_resp.data["id"]
        detail_id = post_resp.data["details"][0]["id"]
        patch_url = reverse("offer-detail", args=[offer_id])

        # Attempt to patch with duplicate offer_type in details
        new_details = [
            {"id": detail_id, "title": "Basic Updated", "revisions": 2,
             "delivery_time_in_days": 4, "price": 60, "features": ["A", "X"], "offer_type": "basic"},
            {"title": "Standard New", "revisions": 3,
             "delivery_time_in_days": 6, "price": 120, "features": ["A", "B", "Y"], "offer_type": "basic"},
        ]
        resp = self.client.patch(
            patch_url, {"details": new_details}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_400_invalid_field_values_in_details(self):
        # Create an offer first
        post_resp = self.client.post(self.list_url, self._payload(), format="json")
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        offer_id = post_resp.data["id"]
        detail_id = post_resp.data["details"][0]["id"]
        patch_url = reverse("offer-detail", args=[offer_id])

        bad_cases = [
            {"id": detail_id, "revisions": -1},
            {"id": detail_id, "delivery_time_in_days": 0},
            {"id": detail_id, "price": -10},
            {"id": detail_id, "features": "not-a-list"},
        ]
        for bad in bad_cases:
            with self.subTest(bad=bad):
                resp = self.client.patch(
                    patch_url, {"details": [bad]}, format="json"
                )
                self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_404_no_offer_with_this_id(self):
        patch_url = reverse("offer-detail", args=[999])
        resp = self.client.patch(patch_url, {"title": "New Title"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)