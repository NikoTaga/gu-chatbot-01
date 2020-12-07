from typing import TYPE_CHECKING

import stripe
from stripe.error import SignatureVerificationError

from billing.exceptions import UpdateCompletedCheckoutError
from billing.models import Checkout
from billing.stripe.stripe_entities import StripeCheckout
from bot.notify import send_payment_completed
from constants import SITE_URL
from shop.models import Product
from billing.constants import StripePaymentMethod, StripeCurrency, StripeMode, STRIPE_SECRET_KEY, STRIPE_WHSEC_KEY, \
    PaymentSystems
from billing.common import PaymentSystemClient

if TYPE_CHECKING:
    from django.http import HttpRequest


class StripeClient(PaymentSystemClient):
    """Клиент платёжной системы Stripe.

    Содержит функции для инициализации сессии и обработки платежей в виде Stripe Payment -
    выписки, захвата, верификации и завершения."""

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
            'success_url': f'{SITE_URL}/billing/payment_success/{order_id}',
            'cancel_url': f'{SITE_URL}/billing/payment_cancel/{order_id}',
        }
        stripe_checkout = StripeCheckout.Schema().load(checkout_data)
        checkout_session = self.client.checkout.Session.create(**stripe_checkout.Schema().dump(stripe_checkout))
        Checkout.objects.make_checkout(PaymentSystems.STRIPE.value, checkout_session.id, order_id)

        return checkout_session.id

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
    def capture(self, checkout_id: str) -> None:
        """Функция-филлер, для унификации процессинга с PayPal."""

        Checkout.objects.update_capture(checkout_id, checkout_id)

    def fulfill(self, checkout_id: str) -> None:
        """Завершает заказ, уведомляет клиента."""

        try:
            checkout = Checkout.objects.fulfill_checkout(checkout_id)
            send_payment_completed(checkout)
        except UpdateCompletedCheckoutError as e:
            print(e)
