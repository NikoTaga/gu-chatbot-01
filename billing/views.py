import json
from pprint import pprint
from django.http import HttpRequest, HttpResponse
# чтобы разрешить кросс-сайт POST запросы
from django.views.decorators.csrf import csrf_exempt

from constants import OrderStatus
from billing.stripe.stripe import StripeClient
from billing.paypal.paypal import PaypalClient
from .models import Checkout
from shop.models import Order
from .constants import STRIPE_PUBLIC_KEY


@csrf_exempt  # type: ignore
def paypal_webhook(request: HttpRequest) -> HttpResponse:
    pp_client = PaypalClient()
    if pp_client.verify(request):
        print('>>> VERIFIED')
        obj = json.loads(request.body)
        pprint(obj)
        if obj['event_type'] == 'CHECKOUT.ORDER.APPROVED':
            checkout_id = obj['resource']['id']
            co_entity = Checkout.get_checkout(checkout_id).first()
            if co_entity and co_entity.order.status != OrderStatus.COMPLETE.value:
                pp_client.capture(checkout_id)
                print('>>> CAPTURED')
                Order.objects.update_order(co_entity.order.pk, OrderStatus.COMPLETE.value)
            elif not co_entity:
                print('The order was modified in process and payment is not valid anymore.')
            elif co_entity.order.status == OrderStatus.COMPLETE.value:
                print('>>> DUPLICATE NOTIFICATION')

    return HttpResponse('OK')


@csrf_exempt  # type: ignore
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    stripe_client = StripeClient()
    if stripe_client.verify(request):
        # OK Signature
        print('>>> VERIFIED')
        obj = json.loads(request.body)
        pprint(obj)
        if obj['type'] == 'checkout.session.completed':
            checkout_id = obj['data']['object']['id']
            co_entity = Checkout.get_checkout(checkout_id).first()
            if co_entity and co_entity.order.status != OrderStatus.COMPLETE.value:
                print('>>> CAPTURED')
                Order.objects.update_order(co_entity.order.pk, OrderStatus.COMPLETE.value)
            elif not co_entity:
                print('The order was modified in process and payment is not valid anymore.')
            elif co_entity.order.status == OrderStatus.COMPLETE.value:
                print('>>> DUPLICATE NOTIFICATION')

        return HttpResponse(status=200)
    else:
        # Failed signature verification
        return HttpResponse(status=400)


def stripe_redirect(request: HttpRequest, cid: str) -> HttpResponse:
    content = {
        'public_key': STRIPE_PUBLIC_KEY,
        'checkout_id': cid,
    }

    return render(request, 'billing/stripe_redirect.html', context=content)
