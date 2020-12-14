"""Модуль содержит менеджеры моделей платёжных систем."""
import logging
from typing import Optional, Union, TYPE_CHECKING

from django.db import models
from django.db.models.query import QuerySet

from billing.exceptions import UpdateCompletedCheckoutError
from shop.models import Order
from common.constants import OrderStatus, PaymentSystem
from billing.constants import PaypalOrderStatus

if TYPE_CHECKING:
    from billing.models import Checkout


logger = logging.getLogger('root')


class CheckoutManager(models.Manager):
    """Менеджер управляет выписанными Checkout."""

    def make_checkout(self,
                      payment_system: PaymentSystem,
                      tracking_id: Union[str, int],
                      order_id: int,
                      payment_status: Optional[str] = None) -> None:
        """Создаёт чекаут, обновляет статус соответствующего заказа"""

        order = Order.objects.get_order(order_id).first()
        Order.objects.update_order(order_id, OrderStatus.PENDING_PAYMENT.value)
        checkout = self.create(order=order, system=payment_system.value, tracking_id=tracking_id, status=payment_status)
        return checkout

    def get_checkout(self, checkout_id: Union[str, int]) -> QuerySet:
        # ToDo: change return value and everything related
        return self.filter(tracking_id=checkout_id)

    def get_checkout_by_capture(self, capture_id: Union[str, int]) -> QuerySet:
        """Получает чекаут по идентификатору, предназначенному для захвата денежных средств
        на счёт магазина."""

        return self.filter(capture_id=capture_id)

    def update_checkout(self, checkout_id: Union[str, int], payment_status: str) -> None:
        """Обновляет статус чекаута после получения сообщений от платёжной системы."""

        checkout = self.get_checkout(checkout_id).first()
        if checkout.status == 'COMPLETED':
            raise UpdateCompletedCheckoutError(
                checkout.pk, checkout.system, checkout.tracking_id, payment_status
            )
        checkout.status = payment_status
        checkout.save()

        return checkout

    def update_capture(self, checkout_id: Union[str, int], capture_id: str) -> 'Checkout':
        """Устанавливает идентификатор для захвата денег на счёт магазина."""

        checkout = self.get_checkout(checkout_id).first()
        checkout.capture_id = capture_id
        checkout.save()

        return checkout

    def fulfill_checkout(self, capture_id: str) -> 'Checkout':
        """Завершает работу с чекаутом, устанавливает статусы ему и заказу в COMPLETE.

        Возвращает инстанс чекаута."""

        co_entity = self.get_checkout_by_capture(capture_id).first()

        if co_entity and co_entity.order.status != OrderStatus.COMPLETE.value:
            # Todo: fix: request.resource.id is not same as the Checkout.tracking_id
            self.update_checkout(co_entity.tracking_id, PaypalOrderStatus.COMPLETED.value)
            Order.objects.update_order(co_entity.order.pk, OrderStatus.COMPLETE.value)
        elif not co_entity:
            # todo raise ordermodifederror
            logger.error(f'Invalid payment, order deleted or modified: {capture_id}')
        elif co_entity.order.status == OrderStatus.COMPLETE.value:
            logger.warning(f'Duplicate notification: {capture_id}')

        return co_entity
