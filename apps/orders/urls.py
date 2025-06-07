from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerOrderViewSet,
    ExecutorOrderListViewSet,
    TakeOrderViewSet,
    OrderDetailAPI
)

router = DefaultRouter()

# Заказчик — CRUD заказов
router.register(r'customer/orders', CustomerOrderViewSet, basename='customer-orders')

# Исполнитель — список доступных заказов
router.register(r'executor/orders', ExecutorOrderListViewSet, basename='executor-orders')

# Исполнитель — оплата и взятие заказа
router.register(r'orders', TakeOrderViewSet, basename='orders-actions')

# Детальный просмотр заказа (например, для карты или фронта)
router.register(r'orders/detail', OrderDetailAPI, basename='order-detail')

urlpatterns = [
    path('', include(router.urls)),
]
