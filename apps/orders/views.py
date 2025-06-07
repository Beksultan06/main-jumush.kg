from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction

from apps.orders.models import Orders
from apps.orders.serializers import OrderSerializer
from apps.users.permissions import IsCustomerPermission, IsExecutorPermission


class CustomerOrderViewSet(viewsets.ModelViewSet):
    """
    Заказчик может создавать и просматривать свои заказы.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def get_queryset(self):
        return Orders.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ExecutorOrderListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Исполнитель видит заказы по своему региону, которые ещё не заняты.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsExecutorPermission]

    def get_queryset(self):
        user_region = self.request.user.region
        return Orders.objects.filter(is_taken=False, region=user_region)


class TakeOrderViewSet(viewsets.GenericViewSet):
    """
    Исполнитель может оплатить и принять заказ.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsExecutorPermission]
    queryset = Orders.objects.all()

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
                return Response({"detail": "Сначала оплатите заказ."}, status=status.HTTP_402_PAYMENT_REQUIRED)

            order.executor = request.user
            order.is_taken = True
            order.save()

            return Response({"detail": "Вы успешно приняли заказ. Контактный номер заказчика: " + order.contact_phone})


class OrderDetailAPI(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    """
    Получение подробной информации о заказе (например, для карты или модалки).
    """
    serializer_class = OrderSerializer
    queryset = Orders.objects.all()
    permission_classes = [IsAuthenticated]
