import json
from pprint import pprint
from django.http import HttpRequest, HttpResponse
# чтобы разрешить кросс-сайт POST запросы
from django.views.decorators.csrf import csrf_exempt
from paypalrestsdk.notifications import WebhookEvent

from constants import OrderStatus
from billing.paypal.paypal import PaypalClient
from .models import Checkout
from shop.models import Order


@csrf_exempt  # type: ignore
def paypal_webhook(request: HttpRequest) -> HttpResponse:
    print('RECEIVED A WEBHOOK')
    h = request.headers
    pprint(h)
    transmission_id = h['Paypal-Transmission-Id']
    timestamp = h['Paypal-Transmission-Time']
    actual_sig = h['Paypal-Transmission-Sig']
    webhook_id = '98W08433SC026140M'
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
        print('>>> VERIFIED')
        obj = json.loads(request.body)
        pprint(obj)
        if obj['event_type'] == 'CHECKOUT.ORDER.APPROVED':
            checkout_id = obj['resource']['id']
            co_entity = Checkout.get_checkout(checkout_id).first()
            if co_entity and co_entity.order.status != OrderStatus.COMPLETE.value:
                PaypalClient().capture(checkout_id)
                print('>>> CAPTURED')
                Order.objects.update_order(co_entity.order.pk, OrderStatus.COMPLETE.value)
            elif not co_entity:
                print('The order was modified in process and payment is not valid anymore.')
            elif co_entity.order.status == OrderStatus.COMPLETE.value:
                print('>>> DUPLICATE NOTIFICATION')


        return HttpResponse('OK')
