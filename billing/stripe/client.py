from typing import TYPE_CHECKING, Dict, Any

import stripe
from stripe.error import SignatureVerificationError

from billing.exceptions import UpdateCompletedCheckoutError
from billing.models import Checkout
from billing.stripe.stripe_entities import StripeCheckout
from bot.notify import send_payment_completed
from shop.models import Product
from billing.constants import StripePaymentMethod, StripeCurrency, StripeMode, STRIPE_SECRET_KEY, STRIPE_WHSEC_KEY, \
    SITE_HTTPS_URL
from common.constants import PaymentSystem
from billing.abstract import PaymentSystemClient
from common.strings import StripeStrings

if TYPE_CHECKING:
    from django.http import HttpRequest


class StripeClient(PaymentSystemClient):
    """Клиент платёжной системы Stripe.

    Содержит функции для инициализации сессии и обработки платежей в виде Stripe Payment -
    выписки, захвата, верификации и завершения."""

    _link_pattern: str = StripeStrings.LINK_PATTERN.value

    def __init__(self) -> None:
        """Инициирует сессию с системой Stripe."""
        self.client = stripe
        self.client.api_key = STRIPE_SECRET_KEY

    def check_out(self, order_id: int, product_id: int) -> str:
        """Создаёт Payment по параметрам заказа, возвращает соответствующий checkout_session.id"""

        product = Product.objects.get_product_by_id(product_id)
        checkout_data = {
            'payment_method_types': [StripePaymentMethod.CARD.value],
            'line_items': [
                {
                    'price_data': {
                        'currency': StripeCurrency.RUB.value,
                        'unit_amount': product['price'].amount * 100,  # подобрать лучший формат
                        'product_data': {
                            'name': product['name'],
                            'description': product['description'],
                        }
                    },
                    'quantity': 1,
                },
            ],
            'mode': StripeMode.PAYMENT,
            'success_url': StripeStrings.LINK_SUCCESS.value.format(site=SITE_HTTPS_URL, order_id=order_id),
            'cancel_url': StripeStrings.LINK_CANCEL.value.format(site=SITE_HTTPS_URL, order_id=order_id),
        }
        stripe_checkout = StripeCheckout.Schema().load(checkout_data)
        checkout_session = self.client.checkout.Session.create(**stripe_checkout.Schema().dump(stripe_checkout))
        Checkout.objects.make_checkout(PaymentSystem.STRIPE, checkout_session.id, order_id)

        approve_link = self._link_pattern.format(site=SITE_HTTPS_URL, session=checkout_session.id)

        return approve_link

    def verify(self, request: 'HttpRequest') -> bool:
        """Проверяет соответствие подписи вебхука на случай попытки имитации оповещения.

        Возвращает результат проверки."""

        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']

        try:
            self.client.Webhook.construct_event(
                payload, sig_header, STRIPE_WHSEC_KEY
            )
        except ValueError:
            # Invalid payload
            return False
        except SignatureVerificationError:
            return False

        return True

    # todo возможно, не самое удачное решение
    def capture(self, wh_data: Dict[str, Any]) -> None:
        """Функция-филлер, для унификации процессинга с PayPal."""
        checkout_id = wh_data['data']['object']['id']
        Checkout.objects.update_capture(checkout_id, checkout_id)

    def fulfill(self, wh_data: Dict[str, Any]) -> None:
        """Завершает заказ, уведомляет клиента."""

        checkout_id = wh_data['data']['object']['id']
        try:
            checkout = Checkout.objects.fulfill_checkout(checkout_id)
            send_payment_completed(checkout)
        except UpdateCompletedCheckoutError as e:
            print(e)
