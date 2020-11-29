import stripe
from pprint import pprint

from billing.stripe.stripe_entities import StripeCheckout
from shop.models import Product
from billing.constants import StripePaymentMethod, StripeCurrency, StripeMode, STRIPE_SECRET_KEY, STRIPE_WHSEC_KEY


stripe.api_key = STRIPE_SECRET_KEY


class StripeClient:
    @staticmethod
    def check_out(order_id, product_id):
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
            'success_url': f'http://194.67.90.202:8000/payment_success/{order_id}',
            'cancel_url': f'http://194.67.90.202:8000/payment_cancel/{order_id}',
        }
        stripe_checkout = StripeCheckout.Schema().load(checkout_data)
        try:
            checkout_session = stripe.checkout.Session.create(**stripe_checkout.Schema().dump(stripe_checkout))
            return checkout_session.id
        except Exception as e:
            print(e.args)
            return e

    def verify(self, request) -> bool:
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WHSEC_KEY
            )
        except ValueError as e:
            # Invalid payload
            return False
        except stripe.error.SignatureVerificationError as e:
            return False

        return True
