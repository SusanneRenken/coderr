from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail


class OffersHappyTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.business_user_1 = User.objects.create_user(
            username="business_user_1", email="business_user_1@example.com", password="x"
        )
        Profile.objects.create(user=cls.business_user_1, type="business")

        cls.business_user_2 = User.objects.create_user(
            username="business_user_2", email="business_user_2@example.com", password="x"
        )
        Profile.objects.create(user=cls.business_user_2, type="business")

        def make_offer(user, title, desc, prices, deliveries):
            offer = Offer.objects.create(user=user, title=title, description=desc)
            for (otype, price, days) in zip(
                ["basic", "standard", "premium"], prices, deliveries
            ):
                OfferDetail.objects.create(
                    offer=offer,
                    title=f"{otype.title()} of {title}",
                    revisions=3 if otype == "basic" else (5 if otype == "standard" else 10),
                    delivery_time_in_days=days,
                    price=price,
                    features=["Logo Design", "Briefpapier"] if otype != "basic" else ["Logo Design"],
                    offer_type=otype,
                )
            return offer


        cls.offer1 = make_offer(
            cls.business_user_1,
            "Website Starter",
            "Dein Paket für den Start",
            prices=[50, 90, 150],
            deliveries=[3, 7, 14],
        )
        cls.offer2 = make_offer(
            cls.business_user_1,
            "Website Pro",
            "Das Paket für Profis",
            prices=[120, 180, 250],
            deliveries=[10, 12, 20],
        )
        cls.offer3 = make_offer(
            cls.business_user_2,
            "Logo Basic",
            "Brauchst du ein Logo?",
            prices=[80, 130, 210],
            deliveries=[5, 9, 15],
        )
        cls.offer4 = make_offer(
            cls.business_user_2,
            "Premium Branding",
            "Deine einzigartige Marke",
            prices=[200, 260, 320],
            deliveries=[2, 5, 9],
        )

        cls.list_url = reverse("offer-list")

    def test_get_200_list_all(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 4)

    def test_get_200_filter_creator_id(self):
        resp = self.client.get(self.list_url, {'creator_id': self.business_user_1.id})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 2)
        for offer in resp.data['results']:
            self.assertEqual(offer['user'], self.business_user_1.id)

    def test_get_200_filter_min_price(self):
        resp = self.client.get(self.list_url, {'min_price': 150})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)
        for offer in resp.data['results']:
            self.assertGreaterEqual(offer['min_price'], 150)

    def test_get_200_filter_max_delivery_time(self):
        resp = self.client.get(self.list_url, {'max_delivery_time': 6})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 3)
        for offer in resp.data['results']:
            self.assertLessEqual(offer['min_delivery_time'], 6)

    def test_get_200_filter_combined(self):
        resp = self.client.get(self.list_url, {
            'creator_id': self.business_user_2.id,
            'min_price': 100,
            'max_delivery_time': 5,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)
        for offer in resp.data['results']:
            self.assertEqual(offer['user'], self.business_user_2.id)
            self.assertGreaterEqual(offer['min_price'], 100)
            self.assertLessEqual(offer['min_delivery_time'], 5)

    def test_get_200_search_title(self):
        resp = self.client.get(self.list_url, {'search': 'Premium'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 1)
        self.assertEqual(resp.data['results'][0]['title'], "Premium Branding")

    def test_get_200_search_description(self):
        resp = self.client.get(self.list_url, {'search': 'paket'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['results']), 2)

