from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from products.models import Product

from .models import Order, OrderItem
from .serializers import CreateOrderSerializer, OrderSerializer


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related('items')
        )


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related('items')
        )


class CheckoutView(APIView):
    """تبدیل سبد خرید به سفارش"""
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'detail': 'سبد خرید خالی است.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart_items = list(cart.items.select_related('product'))
        if not cart_items:
            return Response(
                {'detail': 'سبد خرید خالی است.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # قفل کردن محصولات تا همزمان دو نفر موجودی را اشتباه کم نکنند
        products = Product.objects.select_for_update().in_bulk(
            [item.product_id for item in cart_items]
        )

        total = 0
        for item in cart_items:
            product = products[item.product_id]
            if not product.is_active:
                return Response(
                    {'detail': f'محصول «{product.name}» دیگر موجود نیست.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if item.quantity > product.stock:
                return Response(
                    {'detail': f'موجودی «{product.name}» کافی نیست. '
                               f'موجودی فعلی: {product.stock}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            total += product.price * item.quantity

        order = Order.objects.create(
            user=request.user,
            address=serializer.validated_data['address'],
            total_price=total,
        )

        for item in cart_items:
            product = products[item.product_id]
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=product.price,
                quantity=item.quantity,
            )
            product.stock -= item.quantity
            product.save(update_fields=['stock'])

        cart.items.all().delete()

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )