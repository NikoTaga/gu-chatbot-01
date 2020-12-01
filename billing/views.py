import json
from pprint import pprint
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
# чтобы разрешить кросс-сайт POST запросы
from django.views.decorators.csrf import csrf_exempt

from constants import OrderStatus
from billing.stripe.client import StripeClient
from billing.paypal.client import PaypalClient
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
        if obj['event_type']:
            checkout_id = obj['resource']['id']
            Checkout.objects.fulfill_checkout(pp_client, checkout_id, obj['event_type'])

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
            Checkout.objects.fulfill_checkout(stripe_client, checkout_id)

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


def stripe_payment_success(request: HttpRequest, order_id: int) -> HttpResponse:
    content = {
        'title': 'Заказ оплачен успешно!',
        'order': Order.objects.get_order(order_id).first(),
    }

    return render(request, 'billing/stripe_ok.html', context=content)
