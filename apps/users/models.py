from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.db import models
from apps.utils import convert_image_to_webp
import os


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class UserRegion(models.Model):
    title = models.CharField(max_length=155, verbose_name='Регион')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Регионы пользователей'


class UserSubRegion(models.Model):
    title = models.CharField(max_length=155, verbose_name='Подрегион (Район)')
    region = models.ForeignKey(UserRegion, on_delete=models.CASCADE, related_name='subregions')

    def __str__(self):
        return f"{self.region.title} — {self.title}"

    class Meta:
        verbose_name_plural = 'Подрегионы пользователей'


class User(AbstractUser, PermissionsMixin):
    ROLE = (
        ("исполнитель", "исполнитель"),
        ("заказчик", "заказчик"),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=155, choices=ROLE, verbose_name='Тип пользователей')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(max_length=155, verbose_name='Номер телефона')
    is_verified = models.BooleanField(default=False)
    replies_balance = models.PositiveIntegerField(default=0)
    subregion = models.ForeignKey(
        UserSubRegion,
        on_delete=models.SET_NULL,
        related_name='users',
        null=True,
        blank=True,
        verbose_name='Подрегион (район)'
    )
    passport_photo_with_face = models.ImageField(upload_to='passport_photos/with_face/', null=True, blank=True)
    passport_front = models.ImageField(upload_to='passport_photos/front/', null=True, blank=True)
    passport_back = models.ImageField(upload_to='passport_photos/back/', null=True, blank=True)
    executor_balance = models.PositiveIntegerField(default=0, verbose_name='Баланс исполнителя (сом)')

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        fields_to_convert = {
            'passport_photo_with_face': 'passport_photos/with_face/',
            'passport_front': 'passport_photos/front/',
            'passport_back': 'passport_photos/back/',
        }

        changed = False
        for field_name, path in fields_to_convert.items():
            image_field = getattr(self, field_name)
            if image_field and not image_field.name.endswith('.webp'):
                old_path = image_field.path
                webp_filename, webp_content = convert_image_to_webp(image_field, upload_to=path, resize_to=(1200, 1200))
                getattr(self, field_name).save(webp_filename, webp_content, save=False)
                if os.path.exists(old_path):
                    os.remove(old_path)
                changed = True

        if changed:
            super().save(update_fields=list(fields_to_convert.keys()))

    class Meta:
        verbose_name_plural = 'Пользователи'
