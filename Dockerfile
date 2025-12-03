FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 1. Oldin faqat requirements.txt ni ko'chiramiz
COPY requirements.txt .

# 2. Keyin kutubxonalarni o'rnatamiz (Bu qatorda Docker keshlaydi)
RUN pip install --no-cache-dir -r requirements.txt

# entrypoint.sh ni ko'chiramiz
COPY entrypoint.sh /app/entrypoint.sh

# Uni ishga tushirish huquqini beramiz (Linux uchun muhim)
RUN chmod +x /app/entrypoint.sh

# Docker yonganda shu skript ishlasin
CMD ["/app/entrypoint.sh"]