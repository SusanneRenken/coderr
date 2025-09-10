from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .views import OfferViewSet, RetrieveAPIView

router = routers.SimpleRouter()
router.register(r'offers', OfferViewSet)

urlpatterns = [
    path('offerdetails/<int:pk>/', RetrieveAPIView.as_view(), name='offerdetail-detail'),
   
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)