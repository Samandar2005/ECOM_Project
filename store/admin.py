from django.contrib import admin
from .models import Category, Product, Attribute, AttributeValue, ProductVariant

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

# Variantlarni Product ichida tahrirlash uchun
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    show_change_link = True

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantInline] # <-- Mana shu sehri

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'price', 'stock', 'is_active']
    list_filter = ['is_active', 'product']