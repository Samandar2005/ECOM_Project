FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 1. Oldin faqat requirements.txt ni ko'chiramiz
COPY requirements.txt .

# 2. Keyin kutubxonalarni o'rnatamiz (Bu qatorda Docker keshlaydi)
RUN pip install --no-cache-dir -r requirements.txt

# 3. Eng oxirida kodni ko'chiramiz (Kod o'zgarsa ham, tepasini qayta yuklamaydi)
COPY . .

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]