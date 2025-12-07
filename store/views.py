from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category, Product, ProductVariant
from .serializers import CategorySerializer, ProductSerializer, CartItemInputSerializer
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