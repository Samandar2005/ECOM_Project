# 🚀 Enterprise E-Commerce API

This is a high-performance, scalable E-Commerce backend API built with **Django REST Framework**, **Docker**, **Redis**, and **PostgreSQL**. It features a modern microservices-ready architecture including product variants (SKU), high-speed Redis shopping cart, atomic order transactions, asynchronous tasks, and JWT authentication.

## 🛠 Tech Stack

* **Core:** Python 3.10, Django 4.2, Django REST Framework (DRF)
* **Database:** PostgreSQL 15 (Optimized with Indexes)
* **Caching & Broker:** Redis 7 (Used for API Caching, Cart storage, and Celery Broker)
* **Async Tasks:** Celery 5 (Background tasks processing)
* **Authentication:** JWT (SimpleJWT) with Access & Refresh tokens
* **Documentation:** Swagger UI & Redoc (drf-yasg)
* **Infrastructure:** Docker, Docker Compose, Gunicorn, Whitenoise
* **Server Gateway:** Gunicorn with `entrypoint.sh` for auto-migrations

---

## 🔥 Key Features

### 1. 📦 Advanced Product System (SKU & Variants)
Unlike simple e-commerce sites, this project handles complex enterprise-level product logic:
* **Parent/Child Architecture:** Products are parents, and specific items (Variants) are children (e.g., iPhone 15 -> Variant: Blue, 256GB).
* **Dynamic Attributes:** Create any attribute (Size, Material, Color, Memory) dynamically via Admin Panel.
* **SKU Management:** Each variant has its own unique SKU, Stock count, and Price.

### 2. 🛒 High-Performance Shopping Cart (Redis)
* **In-Memory Storage:** The shopping cart is stored in **Redis**, not the SQL Database. This ensures ultra-fast response times and prevents DB bloating.
* **Smart Session Handling:** Works seamlessly for both logged-in users and anonymous guests.
* **Persistence:** Cart data persists for a configured time (e.g., 7 days) even if the user leaves.

### 3. 💳 Secure Order Processing
* **Atomic Transactions:** Uses `transaction.atomic()` to ensure data integrity during checkout. If one item fails, the whole order is rolled back.
* **Data Migration:** Securely moves data from Redis (Cart) to PostgreSQL (Order/OrderItems) upon successful checkout.

### 4. ⚡ Asynchronous Tasks & Caching
* **Celery Workers:** Handles background tasks (like sending email notifications) without blocking the main API thread.
* **API Caching:** Heavy endpoints (like Product Lists) are cached in Redis to handle high traffic loads.

### 5. 🔐 Security & Documentation
* **JWT Auth:** Secure Access and Refresh token system for Frontend/Mobile integration.
* **Swagger UI:** Fully interactive API documentation available at `/swagger/`.

---

## 🚀 Installation & Setup

Prerequisites: **Docker** and **Docker Desktop** must be installed on your machine.

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/django-ecommerce-api.git](https://github.com/YOUR_USERNAME/django-ecommerce-api.git)
cd django-ecommerce-api