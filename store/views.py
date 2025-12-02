from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class CategoryViewSet(ReadOnlyModelViewSet):
    """Kategoriyalarni faqat o'qish uchun (Read Only)"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(ReadOnlyModelViewSet):
    """Mahsulotlarni faqat o'qish uchun"""
    # Faqat aktiv va omborda bor mahsulotlarni ko'rsatamiz
    queryset = Product.objects.filter(is_active=True, in_stock=True)
    serializer_class = ProductSerializer