from rest_framework import serializers

from .models import Payment


class StartPaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()


class VerifyPaymentSerializer(serializers.Serializer):
    authority = serializers.CharField()
    success = serializers.BooleanField(default=True)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'status', 'authority', 'ref_id', 'created_at', 'paid_at']