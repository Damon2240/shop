import uuid

from django.db import models

from orders.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'در انتظار'
        SUCCESS = 'success', 'موفق'
        FAILED = 'failed', 'ناموفق'

    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='payments'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    authority = models.CharField(
        max_length=36, unique=True, default=uuid.uuid4, editable=False
    )
    ref_id = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment {self.authority} ({self.status})'