from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Orders
from .serializers import OrderSerializer
from apps.users.permissions import IsCustomerPermission, IsExecutorPermission


class CustomerOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomerPermission]

    def get_queryset(self):
        return Orders.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ExecutorOrderListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsExecutorPermission]
    queryset = Orders.objects.filter(is_taken=False)


class TakeOrderViewSet(viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsExecutorPermission]
    queryset = Orders.objects.all()

    @action(detail=True, methods=['post'], url_path='take')
    def take_order(self, request, pk=None):
        order = self.get_object()

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

        if order.is_paid:
            return Response({"detail": "Заказ уже оплачен."}, status=status.HTTP_400_BAD_REQUEST)

        order.is_paid = True
        order.save()
        return Response({"detail": "Оплата прошла успешно. Теперь вы можете принять заказ."})
