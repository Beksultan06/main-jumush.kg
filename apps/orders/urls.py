from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerOrderViewSet, ExecutorOrderListViewSet, TakeOrderViewSet

router = DefaultRouter()
router.register(r'customer/orders', CustomerOrderViewSet, basename='customer-orders')
router.register(r'list/orders', ExecutorOrderListViewSet, basename='list-orders')
router.register(r'', TakeOrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
]
