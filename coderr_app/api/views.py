from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from coderr_app.models import Offer
from .serializer import OfferSerializer
from .permissions import IsBusinessUser, IsOfferOwner

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
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

    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class RetrieveAPIView(APIView):
    pass