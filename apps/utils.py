from PIL import Image
from io import BytesIO
import os
from django.core.files.base import ContentFile


def convert_image_to_webp(image_field, upload_to='order/', quality=80, resize_to=None):
    """
    Конвертирует изображение в webp и возвращает ContentFile для сохранения.

    :param image_field: исходный image field (models.ImageField)
    :param upload_to: путь для сохранения (папка внутри MEDIA_ROOT)
    :param quality: качество webp (0-100)
    :param resize_to: tuple(width, height), например (1024, 1024)
    :return: (filename, ContentFile)
    """
    img = Image.open(image_field)
    img = img.convert("RGB")

    if resize_to:
        img.thumbnail(resize_to)

    webp_io = BytesIO()
    img.save(webp_io, format='webp', quality=quality)

    filename_base, _ = os.path.splitext(os.path.basename(image_field.name))
    webp_filename = f"{upload_to}{filename_base}.webp"
    return webp_filename, ContentFile(webp_io.getvalue())
