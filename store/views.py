from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import send_email_task # <-- Biz yozgan task

class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True, in_stock=True)
    serializer_class = ProductSerializer

    # Kesh qo'shish: method_decorator yordamida
    # 60 * 15 = 15 daqiqa davomida ma'lumot Redisda turadi
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 15))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

@api_view(['POST'])
def test_celery_view(request):
    # Foydalanuvchidan emailni olamiz (yoki test@example.com)
    email = request.data.get('email', 'test@example.com')
    
    # DIQQAT: .delay() metodi vazifani Celeryga (Redisga) uzatadi
    # Kod shu yerda to'xtab turmaydi, darhol keyingi qatorga o'tadi!
    send_email_task.delay(email)
    
    return Response({
        "message": "Email yuborish navbatga qo'yildi!",
        "status": "Siz bu xabarni darhol oldingiz, lekin email orqa fonda ketyapti."
    })