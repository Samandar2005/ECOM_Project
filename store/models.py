from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True) # URL uchun (masalan: /phones/)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255) # URL uchun (masalan: /iphone-15-pro/)
    description = models.TextField(blank=True)
    # Pul bilan ishlaganda har doim DecimalField ishlating (Float xato qilishi mumkin)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    image = models.ImageField(upload_to='products/', blank=True)
    is_active = models.BooleanField(default=True) # Mahsulot sotuvdami?
    in_stock = models.BooleanField(default=True)  # Omborda bormi?
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
        # Bir xil slug bir xil bo'lmasligi uchun indekslaymiz
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name