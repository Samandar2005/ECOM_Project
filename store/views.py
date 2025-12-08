from django.utils.decorators import method_decorator
from django.db import transaction
from django.views.decorators.cache import cache_page
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Category, Product, OrderItem, Order, ProductVariant, Review
from .serializers import CategorySerializer, ProductSerializer, CartItemInputSerializer, OrderInputSerializer, ReviewSerializer
from drf_yasg.utils import swagger_auto_schema # <-- Shuni import qiling
from rest_framework.views import APIView
from rest_framework import status
from .cart import Cart
from .tasks import send_email_task

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(ReadOnlyModelViewSet):
    # N+1 muammosini oldini olish uchun prefetch_related ishlatamiz
    # Chunki mahsulot bilan birga variantlarni va atributlarni ham olib kelish kerak
    queryset = Product.objects.prefetch_related('variants', 'variants__attributes').all()
    serializer_class = ProductSerializer

    # Kesh (Redis) - 15 daqiqa
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

# Celery test view (o'zgarishsiz qoladi)
@api_view(['GET', 'POST'])
def test_celery_view(request):
    email = request.data.get('email') or request.query_params.get('email', 'test@example.com')
    send_email_task.delay(email)
    return Response({"message": "Email queuega qo'shildi!"})



class CartAPIView(APIView):
    """
    Savat bilan ishlash APIsi
    """
    
    def get(self, request):
        cart = Cart(request)
        return Response(cart.get_items())

    # Swaggerga aytamiz: "Bu metod CartItemInputSerializer kutadi"
    @swagger_auto_schema(request_body=CartItemInputSerializer) 
    def post(self, request):
        serializer = CartItemInputSerializer(data=request.data)
        
        # Ma'lumot to'g'riligini tekshirish (Validation)
        if serializer.is_valid():
            variant_id = serializer.validated_data['variant_id']
            quantity = serializer.validated_data['quantity']
            
            cart = Cart(request)
            
            try:
                variant = ProductVariant.objects.get(id=variant_id)
            except ProductVariant.DoesNotExist:
                return Response({"error": "Variant topilmadi"}, status=404)
                
            if variant.stock < quantity:
                return Response({"error": "Omborda yetarli mahsulot yo'q"}, status=400)

            cart.add(variant_id, quantity)
            return Response({"message": "Savatga qo'shildi", "cart": cart.get_items()})
        
        return Response(serializer.errors, status=400)

    # Delete uchun ham kichik Input Serializer ishlatsa bo'ladi, 
    # lekin hozircha shunchaki variant_id ni bodyda kutamiz.
    @swagger_auto_schema(request_body=CartItemInputSerializer)
    def delete(self, request):
        cart = Cart(request)
        variant_id = request.data.get('variant_id')
        cart.remove(variant_id)
        return Response({"message": "O'chirildi", "cart": cart.get_items()})
    
class CheckoutAPIView(APIView):
    """
    Professional Checkout:
    - Atomar tranzaksiya
    - Row Locking (Poyga holatiga qarshi)
    - Stock kamaytirish
    - Asinxron Email
    """
    
    @swagger_auto_schema(request_body=OrderInputSerializer)
    def post(self, request):
        serializer = OrderInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
            
        cart = Cart(request)
        cart_data = cart.get_items()
        
        if not cart_data['items']:
            return Response({"error": "Savat bo'sh"}, status=400)
            
        data = serializer.validated_data
        user = request.user if request.user.is_authenticated else None
        
        try:
            # 1. Tranzaksiyani boshlaymiz
            with transaction.atomic():
                # Buyurtma "shapkasini" yaratamiz
                order = Order.objects.create(
                    user=user,
                    full_name=data['full_name'],
                    address=data['address'],
                    phone=data['phone'],
                    total_price=cart_data['total_price'],
                    status='pending' # To'lov qilinmagan
                )
                
                # 2. Har bir mahsulotni aylanib chiqamiz
                for item in cart_data['items']:
                    variant_id = item['variant_id']
                    quantity = item['quantity']
                    
                    # DIQQAT: select_for_update() - bu qatorni bloklaydi!
                    # Boshqa userlar bu variantni o'zgartira olmay turadi.
                    variant = ProductVariant.objects.select_for_update().get(id=variant_id)
                    
                    # Omborni tekshirish
                    if variant.stock < quantity:
                        # Xatolik bo'lsa, butun tranzaksiya bekor qilinadi (Rollback)
                        raise ValueError(f"'{variant.product.name}' omborda yetarli emas. Qoldi: {variant.stock}")
                    
                    # Ombordan ayiramiz
                    variant.stock -= quantity
                    variant.save()
                    
                    # OrderItem yaratamiz
                    OrderItem.objects.create(
                        order=order,
                        variant=variant,
                        quantity=quantity,
                        price=item['price']
                    )
                
                # 3. Agar hammasi o'xshasa, savatni tozalaymiz
                cart.clear()
                
                # 4. Asinxron Email yuborish (Foydalanuvchini kutdirib qo'ymaslik uchun)
                # data['email'] ga xat ketadi
                send_email_task.delay(data['email'])
                
                return Response({
                    "message": "Buyurtma qabul qilindi!",
                    "order_id": order.id,
                    "status": "success"
                }, status=201)

        except ProductVariant.DoesNotExist:
            return Response({"error": "Mahsulot topilmadi"}, status=404)
        except ValueError as e:
            # Omborda yetishmovchilik bo'lsa
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Tizim xatoligi: " + str(e)}, status=500)
        
class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # O'qish tekin, yozish pullik (login bilan)

    def perform_create(self, serializer):
        # Userni requestdan olib, avtomatik biriktiramiz
        user = self.request.user
        product = serializer.validated_data['product']
        
        # Tekshiramiz: Bu user avval bu mahsulotga izoh yozganmi?
        if Review.objects.filter(user=user, product=product).exists():
            raise ValidationError("Siz bu mahsulotga avval izoh qoldirgansiz!")
            
        serializer.save(user=user)
        
