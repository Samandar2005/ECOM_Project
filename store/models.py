from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/', blank=True) # Asosiy rasm
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Narx va Soni endi bu yerda EMAS, Variantda bo'ladi!

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.name

# --- YANGI QISMLAR ---

class Attribute(models.Model):
    """Masalan: Rang, O'lcham, Xotira"""
    name = models.CharField(max_length=50) # e.g. Color

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    """Masalan: Qizil, XL, 128GB"""
    attribute = models.ForeignKey(Attribute, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=50) # e.g. Red

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class ProductVariant(models.Model):
    """Aniq sotiladigan tovar (SKU)"""
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True) # Unikal kod (SH-102-RED)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    
    # Variantning xususiyatlari (Rang: Qizil, O'lcham: XL)
    attributes = models.ManyToManyField(AttributeValue, related_name='variants')
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.product.name} ({self.sku})"