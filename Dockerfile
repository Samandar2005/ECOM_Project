FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Kutubxonalarni o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha kodini ko'chirish
COPY . .

# Entrypointni ko'chirish
COPY entrypoint.sh /app/entrypoint.sh

# Windows formatidagi qatorlarni Linux formatiga o'tkazish (MUHIM!)
RUN sed -i 's/\r$//' /app/entrypoint.sh

# Ruxsat berish
RUN chmod +x /app/entrypoint.sh

# Konteyner yonganda shu skript ishga tushsin
ENTRYPOINT ["/app/entrypoint.sh"]

# Standart buyruq (Lokalda docker-compose buni 'runserver' ga almashtiradi)
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]