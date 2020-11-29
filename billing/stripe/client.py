import stripe
from pprint import pprint

from stripe.error import SignatureVerificationError

from billing.stripe.stripe_entities import StripeCheckout
from constants import SITE_URL
from shop.models import Product
from billing.constants import StripePaymentMethod, StripeCurrency, StripeMode, STRIPE_SECRET_KEY, STRIPE_WHSEC_KEY
from billing.paypal.client import PaymentSystemClient


class StripeClient(PaymentSystemClient):

    def __init__(self):
        self.client = stripe
        self.client.api_key = STRIPE_SECRET_KEY

    def check_out(self, order_id, product_id):
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
        try:
            checkout_session = self.client.checkout.Session.create(**stripe_checkout.Schema().dump(stripe_checkout))
            return checkout_session.id
        except Exception as e:
            print(e.args)
            return e

    def verify(self, request) -> bool:
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = self.client.Webhook.construct_event(
                payload, sig_header, STRIPE_WHSEC_KEY
            )
        except ValueError as e:
            # Invalid payload
            return False
        except SignatureVerificationError as e:
            return False

        return True

    def capture(self, checkout_id):
        return True
