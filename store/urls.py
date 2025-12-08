from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( CategoryViewSet, ProductViewSet, 
                    test_celery_view, CartAPIView, CheckoutAPIView, ReviewViewSet,
                    CreateCheckoutSessionView, stripe_webhook, OrderViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
    path('test-email/', test_celery_view, name='test_email'),
    path('cart/', CartAPIView.as_view(), name='cart'),
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
]