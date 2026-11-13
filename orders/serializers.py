from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'price', 'quantity', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'status', 'status_display', 'total_price',
            'address', 'items', 'created_at',
        ]
        read_only_fields = ['status', 'total_price', 'created_at']


class CreateOrderSerializer(serializers.Serializer):
    address = serializers.CharField(min_length=10)