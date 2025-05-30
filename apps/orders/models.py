from django.db import models
import os
from apps.utils import convert_image_to_webp
from django.conf import settings


class Orders(models.Model):
    title = models.CharField(max_length=155, verbose_name='Заголовка')
    description = models.TextField(verbose_name='Описание')
    image = models.ImageField(upload_to='order/', verbose_name='Фото объявление')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создание')
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders',
        verbose_name='Создатель заказа'
    )
    executor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='taken_orders',
        verbose_name='Исполнитель'
    )
    is_taken = models.BooleanField(default=False, verbose_name='Заказ принят')
    is_paid = models.BooleanField(default=False, verbose_name='Заказ оплачен исполнителем')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        original_image = self.image
        super().save(*args, **kwargs)

        if self.image and not self.image.name.endswith('.webp'):
            webp_filename, webp_content = convert_image_to_webp(original_image, upload_to='order/', resize_to=(1024, 1024))

            old_path = self.image.path 
            self.image.save(webp_filename, webp_content, save=False)

            if os.path.exists(old_path):
                os.remove(old_path)

            super().save(update_fields=['image'])

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
