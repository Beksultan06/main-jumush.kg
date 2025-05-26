import random
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail

def generate_code():
    return str(random.randint(100000, 999999))

def set_reset_code(email, code, expire=600):
    """
    Сохраняем код в Redis с TTL (например, 600 сек = 10 мин)
    Ключ — например "password_reset:<email>"
    """
    key = f"password_reset:{email}"
    cache.set(key, code, timeout=expire)

def get_reset_code(email):
    key = f"password_reset:{email}"
    return cache.get(key)

def delete_reset_code(email):
    key = f"password_reset:{email}"
    cache.delete(key)

def send_reset_code(email, code):
    subject = 'Код для сброса пароля'
    message = f'Ваш код для смены пароля: {code}\nСрок действия кода 10 минут.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        # Логировать ошибку или пробросить кастомное исключение
        print(f"Ошибка при отправке письма: {e}")
