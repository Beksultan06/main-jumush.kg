from django.contrib import admin
from apps.orders.models import Orders

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_by', 'executor']
    list_filter = ['id', 'title', 'created_by', 'executor']
    search_fields = ['id', 'title', 'created_by', 'executor']