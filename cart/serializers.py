from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    line_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'line_total']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price']


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(pk=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError('محصول پیدا نشد.')
        self.context['product'] = product
        return value

    def validate(self, attrs):
        product = self.context['product']
        cart = self.context['cart']
        item = cart.items.filter(product=product).first()
        new_quantity = attrs['quantity'] + (item.quantity if item else 0)
        if new_quantity > product.stock:
            raise serializers.ValidationError(
                {'quantity': f'موجودی کافی نیست. موجودی فعلی: {product.stock}'}
            )
        return attrs


class UpdateCartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem
        fields = ['quantity']

    def validate_quantity(self, value):
        if value > self.instance.product.stock:
            raise serializers.ValidationError(
                f'موجودی کافی نیست. موجودی فعلی: {self.instance.product.stock}'
            )
        return value