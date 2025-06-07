from django.db import models
import os
from apps.utils import convert_image_to_webp
from django.conf import settings
from apps.users.models import UserRegion
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify


class Category(MPTTModel):
    title = models.CharField(max_length=255, verbose_name='Название категории')
    slug = models.SlugField(unique=True, blank=True, verbose_name='Слаг')
    parent = TreeForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительская категория'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')

    class MPTTMeta:
        order_insertion_by = ['title']

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Orders(models.Model):
    title = models.CharField(max_length=155, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

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

    region = models.ForeignKey(UserRegion, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Регион заказа')
    type_orders = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Тип работы (категория)'
    )

    price_for_executor = models.PositiveIntegerField(default=50, verbose_name='Цена для исполнителя (сом)')
    budget = models.PositiveIntegerField(verbose_name='Бюджет')
    deadline = models.DateField(null=True, blank=True, verbose_name='Срок выполнения')
    contact_phone = models.CharField(max_length=20, verbose_name='Контактный номер')

    latitude = models.FloatField(null=True, blank=True, verbose_name='Широта')
    longitude = models.FloatField(null=True, blank=True, verbose_name='Долгота')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderImage(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='order_images/', verbose_name='Фото')

    def save(self, *args, **kwargs):
        original_image = self.image
        super().save(*args, **kwargs)

        if self.image and not self.image.name.endswith('.webp'):
            webp_filename, webp_content = convert_image_to_webp(original_image, upload_to='order_images/', resize_to=(1024, 1024))

            old_path = self.image.path
            self.image.save(webp_filename, webp_content, save=False)

            if os.path.exists(old_path):
                os.remove(old_path)

            super().save(update_fields=['image'])

    class Meta:
        verbose_name = 'Фото заказа'
        verbose_name_plural = 'Фотографии заказов'
