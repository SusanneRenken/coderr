"""Views for coderr_app: offers, offer details, orders and reviews.

Only docstrings and short comments are added in this patch; the view
logic and permissions remain unchanged.
"""

from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min, Avg
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from coderr_app.models import Offer, OfferDetail, Order, Review
from .serializer import (
    OfferSerializer,
    OfferListSerializer,
    OfferDetailSerializer,
    OfferDetailItemSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    ReviewSerializer,
    ReviewPatchSerializer,
)
from .permissions import (
    IsBusinessUser,
    IsOfferOwner,
    IsCustomerUser,
    IsOrderBusinessOwner,
    IsReviewAuthor,
    IsStaffUser,
)
from .pagination import StandardResultsSetPagination
from .filters import OfferFilter, ReviewFilter
from auth_app.models import Profile


class OfferViewSet(viewsets.ModelViewSet):
    """CRUD for Offer objects with filtering, searching and ordering.

    The view dynamically selects a serializer class for list/detail vs
    create/update and enforces permissions per action.
    """

    queryset = Offer.objects.all()

    serializer_class = OfferSerializer
    list_serializer_class = OfferListSerializer
    detail_serializer_class = OfferDetailSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Offer.objects.select_related("user").prefetch_related("details")
        return queryset.annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        elif self.action == 'retrieve':
            return self.detail_serializer_class
        return self.serializer_class

    def get_permissions(self):
        # Map actions to permission classes
        if self.action == "list":
            return [AllowAny()]
        elif self.action == "retrieve":
            return [IsAuthenticated()]
        elif self.action == "create":
            return [IsAuthenticated(), IsBusinessUser()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsOfferOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferDetailsRetrieveAPIView(generics.RetrieveAPIView):
    """Retrieve single OfferDetail item."""

    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailItemSerializer


class OrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    patch_serializer_class = OrderStatusUpdateSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if self.action == "list":
            # Customers see their orders, business users see business orders
            if hasattr(user, 'profile') and user.profile.type == 'customer':
                return Order.objects.filter(customer_user=user).select_related('offer_detail', 'business_user')
            elif hasattr(user, 'profile') and user.profile.type == 'business':
                return Order.objects.filter(business_user=user).select_related('offer_detail', 'customer_user')
            return Order.objects.none()
        return Order.objects.select_related('offer_detail', 'customer_user', 'business_user')

    def get_serializer_class(self):
        if self.action in ['partial_update', 'update']:
            return self.patch_serializer_class
        return self.serializer_class

    def get_permissions(self):
        if self.action == "create":
            return [IsCustomerUser()]
        if self.action in ["update", "partial_update"]:
            return [IsOrderBusinessOwner()]
        if self.action == "destroy":
            return [IsStaffUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        offer_detail_id = serializer.validated_data.pop("offer_detail_id")
        offer_detail = get_object_or_404(OfferDetail, pk=offer_detail_id)

        serializer.save(
            offer_detail=offer_detail,
            customer_user=self.request.user,
            business_user=offer_detail.offer.user,
        )


class OrderCountView(APIView):
    """Return a count of orders for a given business user and status.

    The view is configured via as_view(status=..., count_key=...) in urls.
    """

    permission_classes = [IsAuthenticated]

    status = "in_progress"
    count_key = "order_count"

    def get(self, request, business_user_id: int, *args, **kwargs):
        status_value = getattr(self, "status", kwargs.get("status", "in_progress"))
        count_key = getattr(self, "count_key", kwargs.get("count_key", "order_count"))
        business_user = get_object_or_404(User, pk=business_user_id)
        count = Order.objects.filter(
            business_user=business_user, status=status_value).count()
        return Response({count_key: count})


class ReviewViewSet(viewsets.ModelViewSet):
    """CRUD for reviews with filtering and ordering support."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    patch_serializer_class = ReviewPatchSerializer    
    
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']

    def get_serializer_class(self):
        if self.action in ['partial_update', 'update']:
            return self.patch_serializer_class
        return super().get_serializer_class()


    def get_permissions(self):
        if self.action in ["create"]:
            return [IsCustomerUser()]
        if self.action in ["partial_update", "update", "destroy"]:
            return [IsReviewAuthor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class BaseInfoAPIView(APIView):
    """Public endpoint that returns aggregate base information used by the frontend."""

    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        review_count = Review.objects.count()
        avg = Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0
        average_rating = round(avg, 1)
        business_profile_count = Profile.objects.filter(type="business").count()
        offer_count = Offer.objects.count()

        data = {
            "review_count": review_count,
            "average_rating": average_rating,
            "business_profile_count": business_profile_count,
            "offer_count": offer_count,
        }

        return Response(data)
