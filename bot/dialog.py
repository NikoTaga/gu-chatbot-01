from typing import Dict, Any, List, Callable
from json.decoder import JSONDecodeError

from billing.constants import PaymentSystems
from billing.stripe.client import StripeClient
from billing.paypal.client import PaypalClient
from builders import ECTSDirector
from constants import MessageDirection, MessageContentType, CallbackType, SITE_URL
from entities import EventCommandReceived, Callback, EventCommandToSend

from shop.models import Category, Product, Order
from billing.models import Checkout


# todo rewrite using a builder
class Dialog:
    """Содержит логику взаимодействия бота с пользователем.

    Осуществляет диалог из нескольких этапов, предлагая выбрать категорию, товар, систему оплаты.
    По итогу инициирует выставление счёта в соответствующей системе."""

    def __init__(self) -> None:
        self.callback = None

    def reply(self, event: EventCommandReceived) -> EventCommandToSend:
        """Основной метод класса, формирует словарь-ответ на базе типа и параметров запроса в формате ECR."""

        variants: Dict[CallbackType, Callable[..., None]] = {
            CallbackType.CATEGORY: self.form_product_list,
            CallbackType.PRODUCT: self.form_product_desc,
            CallbackType.ORDER: self.form_order_confirmation,
            CallbackType.PAYPAL: self.make_order,
            CallbackType.STRIPE: self.make_order,
        }

        command = event.payload.command
        try:
            self.callback = Callback.Schema().loads(command)
            result = variants[self.callback.type](event)
        except (JSONDecodeError, KeyError, TypeError) as err:
            print('Dialog.ready():', err.args)
            result = self.form_category_list(event)

        return result

    def form_category_list(self, event: EventCommandReceived) -> EventCommandToSend:
        """Собирает список категорий в виде данных для сообщения с соответствующими кнопками."""
        button_data: List[Dict[str, Any]] = [
            {
                'title': category['name'],
                'id': category['id'],
                'type': CallbackType.CATEGORY,
            } for category in Category.objects.get_categories()][:10]

        msg = ECTSDirector().create_message(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text='Выберите категорию товара:',
            button_data=button_data,
        )

        print(button_data)

        return msg

    def form_product_list(self, event: EventCommandReceived) -> EventCommandToSend:
        """Собирает список продуктов категории в виде данных для сообщения с соответствующими кнопками."""

        category = Category.objects.get_category_by_id(self.callback.id)
        button_data: List[Dict[str, Any]] = [
             {
                 'title': product['name'],
                 'id': product['id'],
                 'type': CallbackType.PRODUCT,
             } for product in Product.objects.get_products(self.callback.id)][:10]

        msg = ECTSDirector().create_message(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text=f'Выберите товар категории \"{category["name"]}\"',
            button_data=button_data,
        )

        print(button_data)

        return msg

    def form_product_desc(self, event: EventCommandReceived) -> EventCommandToSend:
        """Формирует данные для описания выбранного товара с кнопкой 'Заказать'."""

        product = Product.objects.get_product_by_id(self.callback.id)
        text = f'Выбран товар \"{product["name"]}\"' \
               f'\n\nКраткое описание: {product["description"][:500]}' \
               f'\n\nСтоимость: {product["price"]}'
        button_data: List[Dict[str, Any]] = [
            {
                'title': 'Заказать',
                'id': self.callback.id,
                'type': CallbackType.ORDER,
            }]

        msg = ECTSDirector().create_message(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text=text,
            button_data=button_data,
        )

        print(button_data)

        return msg

    def form_order_confirmation(self, event: EventCommandReceived) -> EventCommandToSend:
        """Формирует данные для сообщения с предложением выбрать платёжную систему для оплаты."""

        product = Product.objects.get_product_by_id(self.callback.id)
        text = f'Выбран товар \"{product["name"]}\"' \
               f'\n\nОплатить заказ за {product["price"]} через платёжную систему?'
        button_data: List[Dict[str, Any]] = [
            {
                'title': 'PayPal',
                'id': self.callback.id,
                'type': CallbackType.PAYPAL,
            },
            {
                'title': 'Stripe',
                'id': self.callback.id,
                'type': CallbackType.STRIPE,
            },
        ]

        msg = ECTSDirector().create_message(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text=text,
            button_data=button_data,
        )

        print(button_data)
        return msg

    def make_order(self, event: EventCommandReceived) -> EventCommandToSend:
        """Формирует заказ и готовит данные для сообщения со ссылкой для произведения оплаты пользователем."""

        order = Order.objects.make_order(
            event.chat_id_in_messenger,
            event.bot_id,
            self.callback.id,
        )
        approve_link = ''
        # todo fix duplication
        if self.callback.type == CallbackType.PAYPAL:
            checkout_id = PaypalClient().check_out(order.pk, self.callback.id)
            approve_link = 'https://www.sandbox.paypal.com/checkoutnow?token=%s' % checkout_id
            checkout = Checkout.objects.make_checkout(PaymentSystems.PAYPAL.value, checkout_id, order.pk)
        elif self.callback.type == CallbackType.STRIPE:
            checkout_id = StripeClient().check_out(order.pk, self.callback.id)
            approve_link = '%s/billing/stripe_redirect/%s' % (SITE_URL, checkout_id)
            checkout = Checkout.objects.make_checkout(PaymentSystems.STRIPE.value, checkout_id, order.pk)
        text = f'Оплатите покупку по ссылке\n{approve_link}!'

        msg = ECTSDirector().create_message(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text=text,
        )

        return msg
