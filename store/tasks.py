from celery import shared_task
import time

@shared_task
def send_email_task(email):
    """
    Buyurtma tasdiqlash xati yuborishni simulyatsiya qilish
    """
    print(f"📧 EMAIL PROCESS: {email} ga xat tayyorlanmoqda...")
    
    # 2 soniya "uxlaydi" (Tarmoq kechikishini simulyatsiya qilish)
    time.sleep(2)
    
    # Bu yerda haqiqiy send_mail funksiyasi bo'lishi kerak edi
    # send_mail('Buyurtma #123', 'Sizning buyurtmangiz qabul qilindi', ...)
    
    print(f"✅ EMAIL SENT: {email} ga muvaffaqiyatli yuborildi!")
    return "Done"