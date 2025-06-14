# Generated by Django 4.2 on 2025-06-07 14:14

import apps.users.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserRegion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=155, verbose_name='Регион')),
            ],
            options={
                'verbose_name_plural': 'Регионы пользователей',
            },
        ),
        migrations.CreateModel(
            name='UserSubRegion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=155, verbose_name='Подрегион (Район)')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subregions', to='users.userregion')),
            ],
            options={
                'verbose_name_plural': 'Подрегионы пользователей',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('role', models.CharField(choices=[('исполнитель', 'исполнитель'), ('заказчик', 'заказчик')], max_length=155, verbose_name='Тип пользователей')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('phone', models.CharField(max_length=155, verbose_name='Номер телефона')),
                ('is_verified', models.BooleanField(default=False)),
                ('replies_balance', models.PositiveIntegerField(default=0)),
                ('passport_photo_with_face', models.ImageField(blank=True, null=True, upload_to='passport_photos/with_face/')),
                ('passport_front', models.ImageField(blank=True, null=True, upload_to='passport_photos/front/')),
                ('passport_back', models.ImageField(blank=True, null=True, upload_to='passport_photos/back/')),
                ('executor_balance', models.PositiveIntegerField(default=0, verbose_name='Баланс исполнителя (сом)')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('subregion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='users', to='users.usersubregion', verbose_name='Подрегион (район)')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', apps.users.models.CustomUserManager()),
            ],
        ),
    ]
