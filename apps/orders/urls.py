from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerOrderViewSet, ExecutorOrderListViewSet, TakeOrderViewSet

router = DefaultRouter()
router.register(r'customer/orders', CustomerOrderViewSet, basename='customer-orders')
router.register(r'executor/orders', ExecutorOrderListViewSet, basename='executor-orders')
router.register(r'orders', TakeOrderViewSet, basename='take-orders')

urlpatterns = [
    path('', include(router.urls)),
]
