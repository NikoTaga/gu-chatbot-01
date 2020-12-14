import logging
from pprint import pprint
from typing import Dict, Any

from django.http import HttpRequest

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalhttp import HttpError
from paypalrestsdk.notifications import WebhookEvent

from bot.notify import send_payment_completed
from shop.models import Product
from billing.constants import Currency, PaypalIntent, PaypalShippingPreference, PaypalUserAction, PaypalGoodsCategory, \
    PaypalOrderStatus, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_WEBHOOK_ID
from common.constants import PaymentSystem
from .paypal_entities import PaypalCheckout
from billing.abstract import PaymentSystemClient
from billing.exceptions import UpdateCompletedCheckoutError
from billing.models import Checkout
from common.strings import PayPalStrings


logger = logging.getLogger('root')


class PaypalClient(PaymentSystemClient):
    """Клиент платёжной системы PayPal.

    Содержит методы для инициализации сессии и обработки платежей в виде PayPal Checkout -
    выписки, захвата, верификации и завершения Checkout."""
    _link_pattern = PayPalStrings.LINK_PATTERN.value

    def __init__(self) -> None:
        """Инициализирует сессию работы с системой PayPal."""

        # Creating an environment
        environment = SandboxEnvironment(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET)
        self.client = PayPalHttpClient(environment)
        self.process_notification = {  # todo should this be here?
            PayPalStrings.WEBHOOK_APPROVED.value: self.capture,
            PayPalStrings.WEBHOOK_COMPLETED.value: self.fulfill,
        }

    def fulfill(self, wh_data: Dict[str, Any]) -> None:
        """Завершает заказ, уведомляет клиента."""

        capture_id = wh_data['resource']['id']
        try:
            checkout = Checkout.objects.fulfill_checkout(capture_id)
            send_payment_completed(checkout)
        except UpdateCompletedCheckoutError as e:
            print(e)

    def verify(self, request: HttpRequest) -> bool:
        """Проверяет соответствие подписи вебхука на случай попытки имитации оповещения.

        Возвращает результат проверки."""

        print('RECEIVED A PAYPAL WEBHOOK')
        h = request.headers
        pprint(h)
        transmission_id = h['Paypal-Transmission-Id']
        timestamp = h['Paypal-Transmission-Time']
        actual_sig = h['Paypal-Transmission-Sig']
        webhook_id = PAYPAL_WEBHOOK_ID
        cert_url = h['Paypal-Cert-Url']
        auth_algo = h['PayPal-Auth-Algo']
        if WebhookEvent.verify(
                transmission_id,
                timestamp,
                webhook_id,
                request.body.decode('utf-8'),
                cert_url,
                actual_sig,
                auth_algo
        ):
            return True
        else:
            # raise PayPalVerificationFailed()
            return False

    def capture(self, wh_data: Dict[str, Any]) -> None:
        """Выполняет операции, связанные с захватом средств после платежа"""

        # после выполнения capture приходит второй аналогичный по типу вебхук, содержащий сведения об оплате
        # todo вообще говоря, следует здесь сверять данные по позиции и сумме, а также комиссии
        if 'payments' in wh_data['resource']['purchase_units'][0]:
            return

        checkout_id = wh_data['resource']['id']
        # if we call for a capture, then the customer has approved a payment for it
        Checkout.objects.update_checkout(checkout_id, PaypalOrderStatus.APPROVED.value)
        # Here, OrdersCaptureRequest() creates a POST request to /v2/checkout/orders
        request = OrdersCaptureRequest(checkout_id)

        # todo выделить в отдельный метод
        try:
            # Call API with your client and get a response for your call
            response = self.client.execute(request)

            # If call returns body in response, you can get the deserialized version
            # from the result attribute of the response
            order = response.result.id
            result = response.status_code
            if response.status_code == 201:
                capture_id = response.result.purchase_units[0].payments.captures[0].id
                Checkout.objects.update_capture(checkout_id, capture_id)
            print(order, result)
        except IOError as ioe:
            if isinstance(ioe, HttpError):
                # Something went wrong server-side
                print(ioe.status_code)
                print(ioe.headers)
                print(ioe)
            else:
                # Something went wrong client side
                print(ioe)

    def _initiate_payment_system_checkout(self, checkout_data: Dict[str, Any]) -> str:
        """Создаёт чекаут в системе PayPal, возвращает его id."""

        pp_capture = PaypalCheckout.Schema().load(checkout_data)

        request = OrdersCreateRequest()
        request.prefer('return=representation')
        request.request_body(pp_capture.Schema().dump(pp_capture))

        tracking_id: str = ''
        try:
            response = self.client.execute(request)
            if response.result.status == PaypalOrderStatus.CREATED.value:
                tracking_id = response.result.id
            else:
                print(response.status_code)
                for link in response.result.links:
                    logger.debug('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
                    logger.debug('Total Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                                              response.result.purchase_units[0].amount.value))
                    # If call returns body in response, you can get the deserialized version
                    # from the result attribute of the response
                    order = response.result
                    logger.debug(order)
        except IOError as ioe:
            logger.error(f'Paypal failed Checkout creation{ioe}')
            if isinstance(ioe, HttpError):
                # Something went wrong server-side
                logger.error(ioe.status_code)

        return tracking_id

    def check_out(self, order_id: int, product_id: int) -> str:
        """Создаёт Checkout по параметрам заказа, возвращает соответствующий tracking_id."""

        # todo create a builder?
        product = Product.objects.get_product_by_id(product_id)
        checkout_data = {
            'intent': PaypalIntent.CAPTURE,
            'purchase_units': [{
                'reference_id': str(order_id),
                'description': product['description'][:127],
                'amount': {
                    'currency_code': Currency.RUB,
                    'value': str(product['price'].amount),
                    'breakdown': {
                        'item_total': {
                            'currency_code': Currency.RUB,
                            'value': str(product['price'].amount),
                        }
                    },
                },
                'items': [
                    {
                        'name': product['name'],
                        'description': product['description'][:127],
                        'unit_amount': {
                            'currency_code': Currency.RUB,
                            'value': str(product['price'].amount),
                        },
                        'quantity': 1,
                        'category': PaypalGoodsCategory.PHYSICAL_GOODS,
                    }
                ]
            }],
            'application_context': {
                'shipping_preference': PaypalShippingPreference.GET_FROM_FILE,
                'user_action': PaypalUserAction.PAY_NOW,
            }
        }

        checkout_id = self._initiate_payment_system_checkout(checkout_data)
        Checkout.objects.make_checkout(PaymentSystem.PAYPAL, checkout_id, order_id)

        approve_link = self._link_pattern.format(checkout_id=checkout_id)

        return approve_link
