import django_filters
from coderr_app.models import Offer, Review

class OfferFilter(django_filters.FilterSet):
    creator_id = django_filters.NumberFilter(field_name="user_id")
    min_price = django_filters.NumberFilter(field_name="min_price", lookup_expr="gte")
    max_delivery_time = django_filters.NumberFilter(field_name="min_delivery_time", lookup_expr="lte")

    class Meta:
        model = Offer
        fields = ["creator_id", "min_price", "max_delivery_time"]

class ReviewFilter(django_filters.FilterSet):
    business_user_id = django_filters.NumberFilter(field_name="business_user_id")
    reviewer_id = django_filters.NumberFilter(field_name="reviewer_id")

    class Meta:
        model = Review
        fields = ["business_user_id", "reviewer_id"]