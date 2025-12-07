from rest_framework import serializers
from .models import Category, Product, ProductVariant, AttributeValue

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute_name', 'value']

class ProductVariantSerializer(serializers.ModelSerializer):
    # Variantning xususiyatlarini (Color: Red) chiqarish uchun
    attributes = AttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'price', 'stock', 'attributes', 'is_active']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    # Eng muhim joyi: Mahsulot ichida uning variantlarini ko'rsatamiz
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'slug', 'description', 'image', 'variants', 'created_at']