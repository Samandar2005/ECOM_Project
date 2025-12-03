from celery import shared_task
import time

@shared_task
def send_email_task(email):
    """
    Bu funksiya og'ir vazifani simulyatsiya qiladi (masalan, email yuborish).
    """
    print(f"EMAIL YUBORISH BOSHLANDI: {email} ga...")
    time.sleep(5) # 5 soniya kutish (xuddi internet sekinligidek)
    print(f"EMAIL YUBORILDI: {email} ga!")
    return "Muvaffaqiyatli"