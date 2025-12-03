# 🚀 High-Load E-Commerce API

Ushbu loyiha zamonaviy texnologiyalar yordamida qurilgan, yuqori yuklamaga dosh beruvchi **Online Do'kon API** tizimi. Loyihada mikroservis arxitekturasiga yaqin yondashuv, keshlashtirish va asinxron vazifalar amalga oshirilgan.

## 🛠 Texnologiyalar

* **Backend:** Python 3.10, Django 4.2, Django Rest Framework (DRF)
* **Database:** PostgreSQL 15
* **Cache & Broker:** Redis 7
* **Asynchronous Tasks:** Celery 5
* **Containerization:** Docker & Docker Compose

## 🔥 Asosiy Imkoniyatlar

1.  **Product & Category API:** To'liq CRUD tizimi (DRF ViewSets).
2.  **Advanced Caching:** Redis yordamida API javoblarini keshlash (100x tezlik).
3.  **Background Tasks:** Email yuborish va og'ir vazifalar Celery orqali asinxron bajariladi.
4.  **Optimized Database:** PostgreSQL indekslari va `select_related` optimizatsiyasi.
5.  **Dockerized:** Bitta buyruq bilan to'liq ishga tushirish.

## 🚀 Ishga tushirish (Installation)

Loyihani kompyuteringizda ishlatib ko'rish uchun **Docker** va **Docker Compose** o'rnatilgan bo'lishi kerak.

1. **Repozitoriyni yuklab olish:**
   ```bash
   git clone [https://github.com/SIZNING_USERNAME/django-ecommerce-api.git](https://github.com/SIZNING_USERNAME/django-ecommerce-api.git)
   cd django-ecommerce-api