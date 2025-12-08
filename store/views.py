import stripe
from django.db import transaction
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, OrderItem, Order, ProductVariant, Review
from .serializers import (CategorySerializer, ProductSerializer, 
                          CartItemInputSerializer, OrderInputSerializer, ReviewSerializer,
                          CreateCheckoutSessionSerializer, OrderSerializer)
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .filters import ProductFilter
from rest_framework.views import APIView
from rest_framework import status
from .cart import Cart
from .tasks import send_email_task
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, IsAdminUser

stripe.api_key = settings.STRIPE_SECRET_KEY

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class OrderViewSet(ModelViewSet):
    """
    Buyurtmalarni boshqarish:
    - Userlar faqat o'z buyurtmalarini ko'radi.
    - Adminlar hammasini ko'radi va statusini o'zgartira oladi.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    # 1. Filtrlash va Qidiruv (Adminlar uchun qulaylik)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['full_name', 'phone', 'id']
    ordering_fields = ['created_at', 'total_price']

    def get_queryset(self):
        user = self.request.user
        # Agar Admin bo'lsa - hamma buyurtmalarni ko'rsin
        if user.is_staff:
            return Order.objects.prefetch_related('items__variant__product').all()
        # Oddiy user faqat o'zining buyurtmalarini ko'rsin
        return Order.objects.prefetch_related('items__variant__product').filter(user=user)

    # Statusni o'zgartirish (faqat qisman update uchun)
    def partial_update(self, request, *args, **kwargs):
        # Agar oddiy user statusni o'zgartirmoqchi bo'lsa, ruxsat bermaslik yoki faqat "cancelled" ga ruxsat berish mumkin
        if not request.user.is_staff:
             return Response({"error": "Siz buyurtmani o'zgartira olmaysiz. Admin bilan bog'laning."}, status=403)
        return super().partial_update(request, *args, **kwargs)

class ProductViewSet(ReadOnlyModelViewSet):
    # Duplikatlarni oldini olish uchun distinct() muhim, 
    # chunki bitta mahsulotning 2 xil varianti narxga to'g'ri kelsa, mahsulot 2 marta chiqib qolishi mumkin.
    queryset = Product.objects.prefetch_related('variants', 'variants__attributes').distinct()
    serializer_class = ProductSerializer
    
    # --- YANGI QISMLAR ---
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # 1. Biz yozgan maxsus filtr klassi
    filterset_class = ProductFilter
    
    # 2. Qidiruv qaysi maydonlarda ishlashi kerak?
    # 'variants__sku' orqali SKU kodini yozsa ham topadi!
    search_fields = ['name', 'description', 'variants__sku']
    
    # 3. Nima bo'yicha saralash mumkin?
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at'] # Default: Yangilari tepada

    # Kesh (Redis) qoladi
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


class CreateCheckoutSessionView(APIView):
    """
    Stripe to'lov havolasini yaratish
    """
    
    # Swaggerga aytamiz: Bu API 'order_id' kutadi
    @swagger_auto_schema(request_body=CreateCheckoutSessionSerializer)
    def post(self, request, *args, **kwargs):
        # Kelgan ma'lumotni tekshiramiz
        serializer = CreateCheckoutSessionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
            
        order_id = serializer.validated_data['order_id']
        
        try:
            order = Order.objects.get(id=order_id)
            
            if order.status == 'paid':
                return Response({"error": "Bu buyurtma allaqachon to'langan"}, status=400)

            # Stripe sessiyasini yaratish
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(order.total_price * 100),
                            'product_data': {
                                'name': f"Order #{order.id} - {order.full_name}",
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url='http://127.0.0.1:8000/api/payment-success/',
                cancel_url='http://127.0.0.1:8000/api/payment-cancel/',
                metadata={
                    "order_id": order.id
                }
            )
            
            return Response({
                "checkout_url": checkout_session.url
            })
            
        except Order.DoesNotExist:
            return Response({"error": "Buyurtma topilmadi. ID to'g'riligini tekshiring."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

@csrf_exempt # CSRF token talab qilinmaydi, chunki buni Stripe yuboradi
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400) # Invalid payload
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400) # Invalid signature

    # To'lov muvaffaqiyatli bo'ldi!
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Metadatadan order_id ni olamiz
        order_id = session['metadata']['order_id']
        
        # Orderni topib, statusini o'zgartiramiz
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'paid'
            order.save()
            print(f"✅ ORDER #{order.id} TO'LANDI!")
        except Order.DoesNotExist:
            print("❌ Order topilmadi")

    return HttpResponse(status=200)


