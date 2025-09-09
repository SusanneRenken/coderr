from django.urls import path, include
from rest_framework import routers
from .views import OfferViewSet, RetrieveAPIView

router = routers.SimpleRouter()
router.register(r'offers', OfferViewSet)

urlpatterns = [
    path('offerdetails/<int:pk>/', RetrieveAPIView.as_view(), name='offerdetail-detail'),
   
    path('', include(router.urls)),
]