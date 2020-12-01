from typing import Optional, Union

from django.db import models
from django.db.models.query import QuerySet

from billing.paypal.client import PaymentSystemClient
from shop.models import Order
from constants import OrderStatus
from billing.constants import PaypalOrderStatus


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

    def fulfill_checkout(self,
                         payment_client: PaymentSystemClient,
                         checkout_id: str,
                         event_type: Optional[str] = None) -> None:

        from bot.dialog import Dialog

        co_entity = self.get_checkout(checkout_id).first()
        if co_entity and co_entity.order.status != OrderStatus.COMPLETE.value:
            if payment_client.capture(checkout_id):
                if event_type == 'CHECKOUT.ORDER.APPROVED':
                    self.update_checkout(checkout_id, PaypalOrderStatus.APPROVED.value)
                    Order.objects.update_order(co_entity.order.pk, OrderStatus.COMPLETE.value)
                    Dialog.send_paypal_payment_completed(co_entity)
                elif event_type == 'PAYMENT.CAPTURE.COMPLETED':
                    # Todo: fix: request.resource.id is not same as the Checkout.tracking_id
                    self.update_checkout(checkout_id, PaypalOrderStatus.COMPLETED.value)
                    Order.objects.update_order(co_entity.order.pk, OrderStatus.COMPLETE.value)
                    Dialog.send_paypal_payment_completed(co_entity)
            else:
                # todo think about how to work with this edge case
                print("Couldn't capture the funds.")
        elif not co_entity:
            print('The order was modified in process and payment is not valid anymore.')
        elif co_entity.order.status == OrderStatus.COMPLETE.value:
            print('>>> DUPLICATE NOTIFICATION')