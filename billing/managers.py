from typing import Optional, Union

from django.db import models
from django.db.models.query import QuerySet

from shop.models import Order
from constants import OrderStatus


class CheckoutManager(models.Manager):
    def make_checkout(self,
                      payment_system: int,
                      tracking_id: Union[str, int],
                      order_id: int,
                      payment_status: Optional[str] = None) -> None:

        order = Order.objects.get_order(order_id).first()
        Order.objects.update_order(order_id, OrderStatus.PENDING_PAYMENT.value)
        checkout = self.create(order=order, system=payment_system, tracking_id=tracking_id, status=payment_status)
        return checkout

    def get_checkout(self, checkout_id: Union[str, int]) -> QuerySet:
        # ToDo: change return value and everything related
        return self.filter(tracking_id=checkout_id)

    def update_checkout(self, checkout_id: Union[str, int], payment_status: str) -> None:
        checkout = self.get_checkout(checkout_id).first()
        checkout.status = payment_status
        checkout.save()
        return checkout
