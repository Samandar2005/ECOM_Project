#!/bin/sh

# Xatolik bo'lsa to'xtash
set -e

# 1. Migratsiya qilish
echo "Migratsiya qilinmoqda..."
python manage.py migrate

# 2. Superuser yaratish (Avtomatik tekshiruv bilan)
echo "Superuser tekshirilmoqda..."
python <<KvK
import os
import django
from django.contrib.auth import get_user_model

django.setup()
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not User.objects.filter(username=username).exists():
    if password:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' muvaffaqiyatli yaratildi!")
    else:
        print("DIQQAT: Superuser paroli topilmadi, yaratilmadi.")
else:
    print(f"Superuser '{username}' allaqachon mavjud. O'tkazib yuborildi.")
KvK

# 3. Serverni ishga tushirish
echo "Server ishga tushmoqda..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000