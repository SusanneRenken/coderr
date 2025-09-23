"""Filter definitions for coderr_app API endpoints.

This module exposes a tiny set of django-filter FilterSets used by the
offers and reviews list endpoints. The public parameter names used by
the API (e.g. `creator_id`, `min_price`, `max_delivery_time`,
`business_user_id`, `reviewer_id`) are intentionally preserved to
match the API documentation and existing client/tests.

Only documentation and comments are added here; the semantic mapping
to model fields is unchanged.
"""

import django_filters
from coderr_app.models import Offer, Review


class OfferFilter(django_filters.FilterSet):
    """Filters available for the `/api/offers/` endpoint.

    Public query params (kept for compatibility with docs/tests):
    - creator_id: filter by the user id who created the offer
    - min_price: offers with a minimum price >= this value (annotated field)
    - max_delivery_time: offers whose minimal delivery time <= this value
      (the view annotates `min_delivery_time` on Offer and tests/clients
      use the name `max_delivery_time` as the query parameter)
    """

    # Filter by the `user_id` (the creator/owner of the Offer)
    creator_id = django_filters.NumberFilter(field_name="user_id")

    # Filter annotated min_price on the Offer queryset (gte)
    min_price = django_filters.NumberFilter(field_name="min_price", lookup_expr="gte")

    # Compatibility: tests/clients send `max_delivery_time` which should
    # compare against the annotated `min_delivery_time` value on Offer.
    max_delivery_time = django_filters.NumberFilter(field_name="min_delivery_time", lookup_expr="lte")

    class Meta:
        model = Offer
        # Expose the public parameter names expected by the API/docs/tests
        fields = ["creator_id", "min_price", "max_delivery_time"]


class ReviewFilter(django_filters.FilterSet):
    """Filters available for the `/api/reviews/` endpoint.

    Public query params:
    - business_user_id: filter reviews written for a specific business user
    - reviewer_id: filter reviews written by a specific reviewer
    These names match the API documentation and test-suite expectations.
    """

    # Filter by the business_user (the recipient of the review)
    business_user_id = django_filters.NumberFilter(field_name="business_user_id")

    # Filter by reviewer id
    reviewer_id = django_filters.NumberFilter(field_name="reviewer_id")

    class Meta:
        model = Review
        fields = ["business_user_id", "reviewer_id"]