import os
from celery import Celery

# Django sozlamalarini standart sifatida belgilash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Sozlamalarni Djangoning settings.py faylidan oladi (CELERY_ bilan boshlanadiganlarini)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Barcha applar ichidagi tasks.py fayllarini avtomatik topadi
app.autodiscover_tasks()