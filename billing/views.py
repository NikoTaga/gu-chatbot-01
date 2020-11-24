import json
from pprint import pprint
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
# чтобы разрешить кросс-сайт POST запросы
from django.views.decorators.csrf import csrf_exempt

from constants import OrderStatus
from .paypal import PaypalClient
from .models import Checkout
from shop.models import Order


@csrf_exempt  # type: ignore
def paypal_webhook(request: HttpRequest) -> HttpResponse:
    obj = json.loads(request.body)
    pprint(obj)
    if obj['event_type'] == 'CHECKOUT.ORDER.APPROVED':
        checkout_id = obj['resource']['id']
        co_entity = Checkout.get_checkout(checkout_id).first()
        if co_entity:
            PaypalClient().capture(checkout_id)
            print('CAPTURED')
            Order.objects.update_order(co_entity.order.pk, OrderStatus.COMPLETE.value)

    return HttpResponse('OK')
