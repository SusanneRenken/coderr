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
            username="biz", email="biz@example.com", password="x"
        )
        Profile.objects.create(user=cls.user, type="business")

    def setUp(self):
        self.client.force_authenticate(self.user)
        self.url = reverse("offer-list")

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

    def test_details_contain_only_id_and_url(self):
        resp = self._post(self._payload())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        list_url = reverse("offer-list")
        resp = self.client.get(list_url)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        details = resp.data["results"][0]["details"]
        self.assertEqual(len(details), 3)
        for d in details:
            self.assertEqual(set(d.keys()), {"id", "url"})

    def test_no_extra_fields_in_user_detail(self):
        self._post(self._payload())
        list_url = reverse("offer-list")
        resp = self.client.get(list_url)
        user_detail = resp.data["results"][0]["user_detail"]
        self.assertEqual(set(user_detail.keys()),
                         {"first_name", "last_name", "username"})

    def test_out_of_range_page_returns_404(self):
        self._post(self._payload())
        list_url = reverse("offer-list") + "?page=999"
        resp = self.client.get(list_url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_page_size_cap_enforced(self):
        for i in range(15):
            self._post(self._payload(title=f"Offer {i}"))
        list_url = reverse("offer-list") + "?page_size=1000"
        resp = self.client.get(list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(resp.data["results"]), 100)

