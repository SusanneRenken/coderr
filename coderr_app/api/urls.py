from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from .views import BaseInfoAPIView, OfferViewSet, OfferDetailsRetrieveAPIView, OrderCountView, OrderViewSet, ReviewViewSet

router = routers.SimpleRouter()
router.register(r'offers', OfferViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('offerdetails/<int:pk>/', OfferDetailsRetrieveAPIView.as_view(),
         name='offerdetail-detail'),
    path(
        'order-count/<int:business_user_id>/',
        OrderCountView.as_view(status='in_progress', count_key='order_count'),
        name="order-count",
    ),
    path(
        'completed-order-count/<int:business_user_id>/',
        OrderCountView.as_view(status='completed', count_key='completed_order_count'),
        name="completed-order-count",
    ),
    path('base-info/', BaseInfoAPIView.as_view(), name='base-info'),
    path('', include(router.urls)),
]
