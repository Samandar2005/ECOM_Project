
# Enterprise E-Commerce API (Yuqori Yuklamali Tizim)

Ushbu loyiha Django REST Framework, Docker, Redis, Celery va PostgreSQL texnologiyalari asosida qurilgan zamonaviy onlayn do'kon (Marketpleys) backend tizimidir.

Loyiha shunchaki CRUD emas, balki "Enterprise" darajasidagi murakkab arxitektura yechimlarini o'z ichiga oladi: Mahsulot variantlari (SKU), Redis orqali tezkor savat, Atomar tranzaksiyalar, Asinxron vazifalar va Stripe to'lov tizimi.

Texnologiyalar (Tech Stack)
- Backend: Python 3.10, Django 4.2, Django REST Framework (DRF)
- Ma'lumotlar Bazasi: PostgreSQL 15 (Indekslash va optimizatsiya bilan)
- Kesh va Broker: Redis 7 (API keshlash, Savatni saqlash va Celery uchun)
- Asinxron Vazifalar: Celery 5
- To'lov Tizimi: Stripe API (Xalqaro to'lovlar)
- Xavfsizlik: JWT (SimpleJWT) - Access va Refresh tokenlar
- Hujjatlashtirish: Swagger UI & Redoc (drf-yasg)
- Infratuzilma: Docker, Docker Compose, Gunicorn, Whitenoise
- Server: entrypoint.sh orqali avtomatik migratsiya va sozlash

Asosiy Imkoniyatlar

1. Murakkab Mahsulot Tizimi (SKU & Variants)
   - Ota-bola (Parent-Child) mantiq
   - Variantlar: rang, xotira, o'lcham va h.k.
   - Dinamik atributlar admin paneldan qo'shiladi
   - Har bir variant alohida SKU, narx va ombor soniga ega

2. Tezkor Savat (Redis)
   - Savat Redis’da saqlanadi → 100 baravar tezkor
   - Ro'yxatdan o'tmagan mehmonlar ham foydalana oladi

3. Xavfsiz Buyurtma va To'lov
   - transaction.atomic() + select_for_update → race condition yo'q
   - Stripe orqali Visa/Mastercard to'lovlari + Webhook

4. Asinxron Vazifalar va Filtrlash
   - Celery bilan email, og'ir hisob-kitoblar orqa fonda
   - django-filter bilan narx, nom, variant bo'yicha qidiruv va saralash

5. Izohlar va Reyting
   - 1-5 gacha baho va izoh qoldirish
   - O'rtacha reyting avtomatik hisoblanadi

O'rnatish va Ishga Tushirish
Talab: Docker va Docker Desktop o'rnatilgan bo'lishi shart.

1. Loyihani yuklab olish
git clone https://github.com/SIZNING_USERNAME/django-ecommerce-api.git
cd django-ecommerce-api

2. .env faylini yaratish
# Windows
copy .env.example .env
# Linux/Mac
cp .env.example .env

(Stripe test kalitlarini .env ga qo'shishni unutmang)

3. Docker orqali ishga tushirish
docker-compose up --build

API Hujjatlari
Server ishga tushgach: http://127.0.0.1:8000/swagger/

Asosiy Endpointlar

Autentifikatsiya
POST /api/token/          → login
POST /api/token/refresh/  → token yangilash

Mahsulotlar (ochiq)
GET  /api/categories/
GET  /api/products/       → ?search=iphone&min_price=100&ordering=-created_at
GET  /api/products/{id}/
POST /api/reviews/        → login talab

Savat (Redis)
GET    /api/cart/
POST   /api/cart/         → {"variant_id": 1, "quantity": 2}
DELETE /api/cart/

Buyurtma
POST /api/checkout/                     → buyurtma yaratish
POST /api/create-checkout-session/      → Stripe to'lov havolasini olish

Test jarayoni (Workflow)
1. /api/token/ → admin / 1234 → token oling
2. Swagger → Authorize → Bearer <token>
3. Mahsulot variant_id sini toping
4. /api/cart/ ga qo'shing
5. /api/checkout/ → order_id oling
6. /api/create-checkout-session/ → Stripe havolasini oling va to'lov qiling
7. /admin/ panelida ombor va buyurtma statusini tekshiring

Muallif
[Sizning Ismingiz] tomonidan ishlab chiqildi.

Pull request va takliflarni kutaman!
