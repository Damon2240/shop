from django.shortcuts import render

# Create your views here.
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import (
    AddToCartSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)


def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_user_cart(request.user)
        return Response(CartSerializer(cart, context={'request': request}).data)


class CartItemAddView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart = get_user_cart(request.user)
        serializer = AddToCartSerializer(
            data=request.data, context={'cart': cart, 'request': request}
        )
        serializer.is_valid(raise_exception=True)

        product = serializer.context['product']
        quantity = serializer.validated_data['quantity']

        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(
            CartSerializer(cart, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_item(self, request, pk):
        # فقط آیتم‌های سبد خود کاربر
        return CartItem.objects.select_related('product').get(
            pk=pk, cart__user=request.user
        )

    def patch(self, request, pk):
        try:
            item = self.get_item(request, pk)
        except CartItem.DoesNotExist:
            return Response({'detail': 'آیتم پیدا نشد.'}, status=404)

        serializer = UpdateCartItemSerializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        cart = get_user_cart(request.user)
        return Response(CartSerializer(cart, context={'request': request}).data)

    def delete(self, request, pk):
        try:
            item = self.get_item(request, pk)
        except CartItem.DoesNotExist:
            return Response({'detail': 'آیتم پیدا نشد.'}, status=404)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartClearView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart = get_user_cart(request.user)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)