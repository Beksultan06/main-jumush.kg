from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Orders
from .serializers import OrderSerializer
from apps.users.permissions import IsCustomerPermission, IsExecutorPermission
from django.db import transaction

class CustomerOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def get_queryset(self):
        user_region = self.request.user.region
        return Orders.objects.filter(is_taken=False, region=user_region)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ExecutorOrderListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsExecutorPermission]

    def get_queryset(self):
        user_region = self.request.user.region
        return Orders.objects.filter(is_taken=False, region=user_region)


class TakeOrderViewSet(viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsExecutorPermission]
    queryset = Orders.objects.all()

    @action(detail=True, methods=['post'], url_path='take')
    def take_order(self, request, pk=None):
        with transaction.atomic():
            try:
                order = Orders.objects.select_for_update().get(pk=pk)
            except Orders.DoesNotExist:
                return Response({"detail": "Заказ не найден."}, status=status.HTTP_404_NOT_FOUND)

            if order.is_taken:
                return Response({"detail": "Этот заказ уже принят."}, status=status.HTTP_400_BAD_REQUEST)

            if not order.is_paid:
                return Response({"detail": "Вы должны оплатить заказ перед тем, как принять его."}, status=status.HTTP_402_PAYMENT_REQUIRED)

            order.executor = request.user
            order.is_taken = True
            order.save()
            return Response({"detail": "Заказ успешно принят."})

    @action(detail=True, methods=['post'], url_path='pay')
    def pay_order(self, request, pk=None):
        order = self.get_object()
        user = request.user

        if order.is_paid:
            return Response({"detail": "Заказ уже оплачен."}, status=status.HTTP_400_BAD_REQUEST)

        if user.executor_balance < order.price_for_executor:
            return Response({
                "detail": "Недостаточно средств. Пополните баланс минимум на 50 сомов.",
                "your_balance": user.executor_balance
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

        user.executor_balance -= order.price_for_executor
        user.save()

        order.is_paid = True
        order.save()

        return Response({
            "detail": f"С вашего баланса списано {order.price_for_executor} сомов. Теперь вы можете принять заказ.",
            "remaining_balance": user.executor_balance
        }, status=status.HTTP_200_OK)

class OrderDetailAPI(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Orders.objects.all
    