from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, test_celery_view, CartAPIView, CheckoutAPIView # <-- Import

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('test-email/', test_celery_view, name='test_email'),
    path('cart/', CartAPIView.as_view(), name='cart'), # <-- Yangi yo'l
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
]