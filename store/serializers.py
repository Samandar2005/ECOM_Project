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


class CartItemInputSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)


class OrderInputSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    address = serializers.CharField(max_length=500)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField() # Emailni ham so'raymiz (mehmonlar uchun)

    def validate_phone(self, value):
        # Oddiy tekshiruv: Raqam juda qisqa bo'lmasligi kerak
        if len(value) < 7:
            raise serializers.ValidationError("Telefon raqam noto'g'ri")
        return value