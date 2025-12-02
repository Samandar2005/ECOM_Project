from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    # Kategoriya ID si emas, uning ma'lumotlari to'liq chiqishi uchun:
    category = CategorySerializer(read_only=True) 

    class Meta:
        model = Product
        fields = ['id', 'category', 'name', 'slug', 'description', 'price', 'image', 'in_stock']