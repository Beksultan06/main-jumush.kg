from django.contrib import admin
from apps.orders.models import Orders
from mptt.admin import DraggableMPTTAdmin
from apps.orders.models import Category

admin.site.register(Category, DraggableMPTTAdmin)

@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_by', 'executor', 'is_paid', 'region', 'type_orders']
    list_filter = ['id', 'title', 'created_by', 'executor', 'is_paid', 'region', 'type_orders']
    search_fields = ['id', 'title', 'created_by', 'executor', 'is_paid', 'region', 'type_orders']