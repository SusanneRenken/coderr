from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min
from rest_framework import viewsets, generics, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from coderr_app.models import Offer, OfferDetail
from .serializer import OfferSerializer, OfferListSerializer, OfferDetailSerializer, OfferDetailItemSerializer
from .permissions import IsBusinessUser, IsOfferOwner
from .pagination import StandardResultsSetPagination
from .filters import OfferFilter

class OfferViewSet(viewsets.ModelViewSet):
    
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
    permission_classes = [IsAuthenticated]