from django.conf import settings
from django.core.cache import cache
from .models import ProductVariant

class Cart:
    def __init__(self, request):
        """
        Savatni initsializatsiya qilish.
        Foydalanuvchi ID si yoki sessiya ID si bo'yicha noyob kalit yaratamiz.
        """
        self.session = request.session
        self.user = request.user
        
        # Agar user login qilgan bo'lsa, uning ID si, bo'lmasa anonim sessiya kaliti
        if self.user.is_authenticated:
            self.cart_id = f"cart_user_{self.user.id}"
        else:
            if not self.session.session_key:
                self.session.create()
            self.cart_id = f"cart_session_{self.session.session_key}"

        # Redisdan savatni olamiz, agar yo'q bo'lsa bo'sh lug'at {}
        self.cart = cache.get(self.cart_id, {})

    def add(self, variant_id, quantity=1):
        """Mahsulot variantini savatga qo'shish"""
        variant_id = str(variant_id)
        
        if variant_id in self.cart:
            self.cart[variant_id] += quantity
        else:
            self.cart[variant_id] = quantity
            
        self.save()

    def remove(self, variant_id):
        """Savatdan o'chirish"""
        variant_id = str(variant_id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def save(self):
        """O'zgarishlarni Redisga saqlash (1 hafta turadi)"""
        cache.set(self.cart_id, self.cart, timeout=60 * 60 * 24 * 7)

    def clear(self):
        """Savatni tozalash"""
        cache.delete(self.cart_id)
        self.cart = {}

    def get_items(self):
        """
        Savatdagi mahsulotlarni to'liq ma'lumotlari bilan qaytarish.
        API uchun tayyorlaymiz.
        """
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids).select_related('product')
        
        items = []
        total_price = 0
        
        for variant in variants:
            qty = self.cart[str(variant.id)]
            total_price += variant.price * qty
            
            # Variantning atributlarini (masalan: Qizil, 256GB) chiroyli qilib olamiz
            attributes = ", ".join([f"{av.attribute.name}: {av.value}" for av in variant.attributes.all()])
            
            items.append({
                "variant_id": variant.id,
                "product_name": variant.product.name,
                "sku": variant.sku,
                "attributes": attributes,
                "price": float(variant.price),
                "quantity": qty,
                "total": float(variant.price * qty),
                "image": variant.product.image.url if variant.product.image else None
            })
            
        return {
            "items": items,
            "total_price": float(total_price),
            "count": sum(self.cart.values())
        }