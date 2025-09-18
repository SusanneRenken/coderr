from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .views import OfferViewSet, OfferDetailsRetrieveAPIView, OrderViewSet

router = routers.SimpleRouter()
router.register(r'offers', OfferViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('offerdetails/<int:pk>/', OfferDetailsRetrieveAPIView.as_view(), name='offerdetail-detail'),
   
    path('', include(router.urls)),
]