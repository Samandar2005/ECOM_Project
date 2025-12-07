from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
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