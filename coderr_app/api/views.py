from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from coderr_app.models import Offer, OfferDetail, Order
from .serializer import OfferSerializer, OfferListSerializer, OfferDetailSerializer, OfferDetailItemSerializer, OrderSerializer, OrderStatusUpdateSerializer
from .permissions import IsBusinessUser, IsOfferOwner, IsCustomerUser, IsOrderBusinessOwner, IsStaffUser
from .pagination import StandardResultsSetPagination
from .filters import OfferFilter


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()

    serializer_class = OfferSerializer
    list_serializer_class = OfferListSerializer
    detail_serializer_class = OfferDetailSerializer

    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Offer.objects.select_related(
            "user").prefetch_related("details")
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
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id: int, *args, **kwargs):
        status_value = kwargs.get("status", "in_progress")
        count_key = kwargs.get("count_key", "order_count")
        business_user = get_object_or_404(User, pk=business_user_id)
        count = Order.objects.filter(business_user=business_user, status=status_value).count()
        return Response({count_key: count})
