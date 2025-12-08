from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    # Narx bo'yicha oraliq (Min - Max)
    # E'tibor bering: Narx Variant ichida, shuning uchun 'variants__price' deymiz
    min_price = filters.NumberFilter(field_name="variants__price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="variants__price", lookup_expr='lte')
    
    # Kategoriya (Slug bo'yicha)
    category = filters.CharFilter(field_name="category__slug", lookup_expr='iexact')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price']