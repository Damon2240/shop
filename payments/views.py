import random

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order

from .models import Payment
from .serializers import (
    PaymentSerializer,
    StartPaymentSerializer,
    VerifyPaymentSerializer,
)


class StartPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StartPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = Order.objects.get(
                pk=serializer.validated_data['order_id'], user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': 'سفارش پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND
            )

        if order.status != Order.Status.PENDING:
            return Response(
                {'detail': 'این سفارش قابل پرداخت نیست.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(order=order, amount=order.total_price)
        return Response(
            PaymentSerializer(payment).data, status=status.HTTP_201_CREATED
        )


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment = Payment.objects.select_for_update().select_related(
                'order'
            ).get(
                authority=serializer.validated_data['authority'],
                order__user=request.user,
            )
        except Payment.DoesNotExist:
            return Response(
                {'detail': 'تراکنش پیدا نشد.'}, status=status.HTTP_404_NOT_FOUND
            )

        if payment.status != Payment.Status.PENDING:
            return Response(
                {'detail': 'این تراکنش قبلاً بررسی شده است.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.validated_data['success']:
            payment.status = Payment.Status.SUCCESS
            payment.ref_id = str(random.randint(10**9, 10**10 - 1))
            payment.paid_at = timezone.now()
            payment.order.status = Order.Status.PAID
            payment.order.save(update_fields=['status', 'updated_at'])
        else:
            payment.status = Payment.Status.FAILED

        payment.save()
        return Response(PaymentSerializer(payment).data)