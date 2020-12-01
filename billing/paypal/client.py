from pprint import pprint
from django.http import HttpRequest
from abc import abstractmethod

from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from paypalcheckoutsdk.orders import OrdersCreateRequest, OrdersValidateRequest
from paypalcheckoutsdk.orders import OrdersCaptureRequest
from paypalhttp import HttpError
from paypalrestsdk.notifications import WebhookEvent

from shop.models import Product
from billing.constants import Currency, PaypalIntent, PaypalShippingPreference, PaypalUserAction, PaypalGoodsCategory, \
    PaypalOrderStatus
from .paypal_entities import PaypalCheckout


class PaymentSystemClient:
    client = None

    @abstractmethod
    def check_out(self, order_id, product_id):
        pass

    @abstractmethod
    def verify(self, request: HttpRequest):
        pass

    @abstractmethod
    def capture(self, checkout_id):
        pass


class PaypalClient(PaymentSystemClient):
    # Creating Access Token for Sandbox
    client_id = "ASQgJpdrDZjvbEgIaViCTuEbO_ef6-JS1Cjy9g0EXwO65OPGdVxWpVd5pM7cvgrXzotENGAB7TEQ6PLK"
    client_secret = "EPZSAbYg0C4Zvp1rZDoacf2rTOyeALHQR2OVmp5RkbS3Ox9p89UcbXd4Sa0LQ3hUDYFZRLB71RKXZZbQ"

    def __init__(self):
        # Creating an environment
        environment = SandboxEnvironment(client_id=self.client_id, client_secret=self.client_secret)
        self.client = PayPalHttpClient(environment)

    def verify(self, request: HttpRequest) -> bool:
        print('RECEIVED A PAYPAL WEBHOOK')
        h = request.headers
        pprint(h)
        transmission_id = h['Paypal-Transmission-Id']
        timestamp = h['Paypal-Transmission-Time']
        actual_sig = h['Paypal-Transmission-Sig']
        webhook_id = '3FH61885KM759214M'
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

    def capture(self, checkout_id: str):
        # Here, OrdersCaptureRequest() creates a POST request to /v2/checkout/orders
        request = OrdersCaptureRequest(checkout_id)

        try:
            # Call API with your client and get a response for your call
            response = self.client.execute(request)

            # If call returns body in response, you can get the deserialized version from the result attribute of the response
            order = response.result.id
            result = response.status_code
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
            return False

        return True if response.status_code == 201 else False

    def check_out(self, order_id: int, product_id: int):
        request = OrdersCreateRequest()
        product = Product.objects.get_product_by_id(product_id)
        request.prefer('return=representation')
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
        pp_capture = PaypalCheckout.Schema().load(checkout_data)
        request.request_body(pp_capture.Schema().dump(pp_capture))

        checkout_id = ''
        try:
            response = self.client.execute(request)
            if response.result.status == PaypalOrderStatus.CREATED.value:
                checkout_id = response.result.id
            else:
                print(response.status_code)
                for link in response.result.links:
                    print('\t{}: {}\tCall Type: {}'.format(link.rel, link.href, link.method))
                    print('Total Amount: {} {}'.format(response.result.purchase_units[0].amount.currency_code,
                                                       response.result.purchase_units[0].amount.value))
                    # If call returns body in response, you can get the deserialized version from the result attribute of the response
                    order = response.result
                    print(order)
        except IOError as ioe:
            print(ioe)
            if isinstance(ioe, HttpError):
                # Something went wrong server-side
                print(ioe.status_code)

        return checkout_id
