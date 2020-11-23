from django.db import models
from djmoney.models.fields import MoneyField

from bot.models import TrackableUpdateCreateModel
from billing.constants import PaymentSystems
from constants import OrderStatus
from shop.models import Order


class Checkout(TrackableUpdateCreateModel):
    order = models.ForeignKey(
        'shop.Order',
        verbose_name='Order',
        # todo обдумать поведение
        on_delete=models.RESTRICT,
    )
    system = models.IntegerField('Billing system', choices=PaymentSystems.choices())
    tracking_id = models.CharField('Tracking id', max_length=255)

    class Meta:
        verbose_name = 'Checkout'
        verbose_name_plural = 'Checkouts'
        app_label = 'billing'
        ordering = ['-created_at']

    @classmethod
    def update_checkout(cls, checkout_id, status):
        # should save some pp processing fields
        checkout = Checkout.get_checkout(checkout_id)

    @classmethod
    def get_checkout(cls, checkout_id):
        return Checkout.objects.filter(tracking_id=checkout_id)

    @classmethod
    def make_checkout(cls, system, tracking_id, order_id):
        order = Order.objects.get_order(order_id).first()
        Order.objects.update_order(order_id, OrderStatus.PENDING_PAYMENT.value)
        cls.objects.create(order=order, system=system, tracking_id=tracking_id)
