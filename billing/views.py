"""Модуль содержит список views, покрывающих функционал billing."""

import json
from pprint import pprint
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
# чтобы разрешить кросс-сайт POST запросы
from django.views.decorators.csrf import csrf_exempt

from billing.stripe.client import StripeClient
from billing.paypal.client import PaypalClient
from shop.models import Order
from .constants import STRIPE_PUBLIC_KEY


@csrf_exempt  # type: ignore
def paypal_webhook(request: HttpRequest) -> HttpResponse:
    """Обрабатывает входящие вебхуки со стороны PayPal и возвращает 200 ОК.

    Проводит верификацию и передаёт клиенту paypal на дальнейшую обработку."""

    pp_client = PaypalClient()
    if pp_client.verify(request):
        print('>>> VERIFIED')
        obj = json.loads(request.body)
        pprint(obj)
        pp_client.process_notification[obj['event_type']](obj)

    return HttpResponse('OK')


@csrf_exempt  # type: ignore
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    """Обрабатывает входящие вебхуки со стороны Stripe и возвращает 200 ОК.

    Проводит верификацию и передаёт клиенту Stripe на дальнейшую обработку."""

    # todo понять, как правильно поделить логику между вью и клиентом
    stripe_client = StripeClient()
    if stripe_client.verify(request):
        # OK Signature
        print('>>> VERIFIED')
        obj = json.loads(request.body)
        if obj['type'] == 'checkout.session.completed':
            pprint(obj)
            checkout_id = obj['data']['object']['id']
            stripe_client.capture(checkout_id)
            stripe_client.fulfill(checkout_id)

        return HttpResponse(status=200)
    else:
        # Failed signature verification
        return HttpResponse(status=400)


def stripe_redirect(request: HttpRequest, cid: str) -> HttpResponse:
    """Формирует редирект с доформированием сессии со стороны JS скрипта stripe."""

    content = {
        'public_key': STRIPE_PUBLIC_KEY,
        'checkout_id': cid,
    }

    return render(request, 'billing/stripe_redirect.html', context=content)


def stripe_payment_success(request: HttpRequest, order_id: int) -> HttpResponse:
    """Сообщает пользователю об успешном проведении оплаты заказа."""

    content = {
        'title': 'Заказ оплачен успешно!',
        'order': Order.objects.get_order(order_id).first(),
    }

    return render(request, 'billing/stripe_ok.html', context=content)
