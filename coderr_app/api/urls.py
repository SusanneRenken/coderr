"""URL routing for coderr_app API endpoints.

The router exposes the standard viewset endpoints and a few custom
paths are registered below (offerdetails, order counts, base info).
"""

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
    # Retrieve a single offer detail item
    path('offerdetails/<int:pk>/', OfferDetailsRetrieveAPIView.as_view(),
         name='offerdetail-detail'),
    # Count endpoints for quick metrics per business user
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
    # Public base info used by the frontend
    path('base-info/', BaseInfoAPIView.as_view(), name='base-info'),
    # Include automatically generated router URLs
    path('', include(router.urls)),
]
