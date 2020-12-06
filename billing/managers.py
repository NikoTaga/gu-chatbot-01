from typing import Optional, Union, TYPE_CHECKING

from django.db import models
from django.db.models.query import QuerySet

from billing.exceptions import UpdateCompletedCheckoutError
from shop.models import Order
from constants import OrderStatus
from billing.constants import PaypalOrderStatus

if TYPE_CHECKING:
    from billing.models import Checkout


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

    def get_checkout_by_capture(self, capture_id: Union[str, int]) -> QuerySet:
        # ToDo: change return value and everything related
        return self.filter(capture_id=capture_id)

    def update_checkout(self, checkout_id: Union[str, int], payment_status: str) -> None:
        checkout = self.get_checkout(checkout_id).first()
        if checkout.status == 'COMPLETED':
            raise UpdateCompletedCheckoutError(
                checkout.pk, checkout.system, checkout.tracking_id, payment_status
            )
        checkout.status = payment_status
        checkout.save()

        return checkout

    def update_capture(self, checkout_id: Union[str, int], capture_id: str) -> Checkout:
        checkout = self.get_checkout(checkout_id).first()
        checkout.capture_id = capture_id
        checkout.save()

        return checkout

    def fulfill_checkout(self, capture_id: str) -> 'Checkout':

        co_entity = self.get_checkout_by_capture(capture_id).first()

        if co_entity and co_entity.order.status != OrderStatus.COMPLETE.value:
            # Todo: fix: request.resource.id is not same as the Checkout.tracking_id
            self.update_checkout(co_entity.tracking_id, PaypalOrderStatus.COMPLETED.value)
            Order.objects.update_order(co_entity.order.pk, OrderStatus.COMPLETE.value)
        elif not co_entity:
            print('The order was modified in process and payment is not valid anymore.')
        elif co_entity.order.status == OrderStatus.COMPLETE.value:
            print('>>> DUPLICATE NOTIFICATION')

        return co_entity
