from rest_framework import viewsets
from rest_framework.views import APIView
from coderr_app.models import Offer
from .serializer import OfferSerializer

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

class RetrieveAPIView(APIView):
    pass