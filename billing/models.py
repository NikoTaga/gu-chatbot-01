from django.db import models

from bot.models import TrackableUpdateCreateModel
from billing.constants import PaymentSystems, PaypalOrderStatus
from shop.models import Order
from .managers import CheckoutManager


class Checkout(TrackableUpdateCreateModel):
    order = models.ForeignKey(
        'shop.Order',
        verbose_name='Order',
        # todo обдумать поведение
        on_delete=models.RESTRICT,
    )
    system = models.IntegerField('Billing system', choices=PaymentSystems.choices())
    tracking_id = models.CharField('Tracking id', max_length=255)
    status = models.CharField(
        'Status',
        max_length=200,
        null=True,
        blank=True
    )
    objects = CheckoutManager()

    class Meta:
        verbose_name = 'Checkout'
        verbose_name_plural = 'Checkouts'
        app_label = 'billing'
        ordering = ['-created_at']
