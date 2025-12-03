from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True, in_stock=True)
    serializer_class = ProductSerializer

    # Kesh qo'shish: method_decorator yordamida
    # 60 * 15 = 15 daqiqa davomida ma'lumot Redisda turadi
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)