# Generated by Django 4.2 on 2025-05-30 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='is_paid',
            field=models.BooleanField(default=False, verbose_name='Заказ оплачен исполнителем'),
        ),
    ]
