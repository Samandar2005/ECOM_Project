#!/bin/sh

# Xatolik bo'lsa to'xtash
set -e

# 1. Migratsiya qilish
echo "🔄 Migratsiya jarayoni boshlandi..."
python manage.py migrate --noinput

# 2. Statik fayllarni yig'ish (faqat kerak bo'lsa, xatolik bermasligi uchun)
# echo "📦 Statik fayllar yig'ilmoqda..."
# python manage.py collectstatic --noinput

# 3. Superuser yaratish (Avtomatik)
echo "👤 Superuser tekshirilmoqda..."
python <<KvK
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '1234')

if not User.objects.filter(username=username).exists():
    if password:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✅ Superuser '{username}' muvaffaqiyatli yaratildi!")
    else:
        print("⚠️ DIQQAT: Superuser paroli topilmadi, yaratilmadi.")
else:
    print(f"ℹ️ Superuser '{username}' allaqachon mavjud.")
KvK

# 4. Asosiy buyruqni ishga tushirish (runserver yoki gunicorn)
echo "🚀 Server ishga tushmoqda..."
exec "$@"