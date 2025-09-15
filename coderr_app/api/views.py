from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from coderr_app.models import Offer
from .serializer import OfferSerializer, OfferListSerializer, OfferDetailSerializer
from .permissions import IsBusinessUser, IsOfferOwner
from .pagination import StandardResultsSetPagination

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.select_related('user').prefetch_related('details')

    serializer_class = OfferSerializer
    list_serializer_class = OfferListSerializer
    detail_serializer_class = OfferDetailSerializer

    parser_classes = [JSONParser, MultiPartParser, FormParser]
    pagination_class = StandardResultsSetPagination

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

class OfferDetailsRetrieveAPIView(APIView):
    pass