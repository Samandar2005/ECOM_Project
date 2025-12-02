from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)} # Ismini yozganda slug avtomatik yoziladi

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'in_stock', 'is_active', 'created_at']
    list_filter = ['in_stock', 'is_active']
    list_editable = ['price', 'in_stock', 'is_active'] # Ro'yxatni o'zidan narxni o'zgartirish
    prepopulated_fields = {'slug': ('name',)}