from typing import Dict, Any, List, Callable
from json.decoder import JSONDecodeError

from billing.constants import PaymentSystems
from billing.stripe.client import StripeClient
from billing.paypal.client import PaypalClient
from constants import MessageDirection, MessageContentType, CallbackType, SITE_URL
from entities import EventCommandReceived, Callback

from shop.models import Category, Product, Order
from billing.models import Checkout


# todo rewrite using a builder
class Dialog:
    """Содержит логику взаимодействия бота с пользователем.

    Осуществляет диалог из нескольких этапов, предлагая выбрать категорию, товар, систему оплаты.
    По итогу инициирует выставление счёта в соответствующей системе."""

    def __init__(self) -> None:
        self.data = None
        self.callback = None

    def reply(self, event: EventCommandReceived) -> Dict[str, Any]:
        """Основной метод класса, формирует словарь-ответ на базе типа и параметров запроса в формате ECR."""

        variants: Dict[CallbackType, Callable[..., None]] = {
            CallbackType.CATEGORY: self.form_product_list,
            CallbackType.PRODUCT: self.form_product_desc,
            CallbackType.ORDER: self.form_order_confirmation,
            CallbackType.PAYPAL: self.make_order,
            CallbackType.STRIPE: self.make_order,
        }
        # начало формирования объекта с данными для ECTS
        self.data = self.form_preset(event)

        command = event.payload.command
        try:
            self.callback = Callback.Schema().loads(command)
            variants[self.callback.type]()
        except (JSONDecodeError, KeyError, TypeError) as err:
            print('Dialog.ready():', err.args)
            self.form_category_list()

        return self.data

    @staticmethod
    def form_preset(event: EventCommandReceived) -> Dict[str, Any]:

        return {
            'bot_id': event.bot_id,
            'chat_id_in_messenger': event.chat_id_in_messenger,
            'payload': {
                'direction': MessageDirection.SENT,
                'text': None,
            },
        }

    def form_category_list(self) -> None:
        """Собирает список категорий в виде данных для сообщения с соответствующими кнопками."""

        self.data['content_type'] = MessageContentType.INLINE
        self.data['payload']['text'] = 'Выберите категорию товара:'
        buttons_data: List[Dict[str, Any]] = [
            {
                'text': category['name'],
                'action': {
                    'type': 'postback',
                    'payload': Callback.Schema().dumps({
                        'type': CallbackType.CATEGORY,
                        'id': category['id']
                    }),
                }
            } for category in Category.objects.get_categories()][:10]
        print(buttons_data)
        self.data['inline_buttons'] = buttons_data

    def form_product_list(self) -> None:
        """Собирает список продуктов категории в виде данных для сообщения с соответствующими кнопками."""

        self.data['content_type'] = MessageContentType.INLINE
        category = Category.objects.get_category_by_id(self.callback.id)
        self.data['payload']['text'] = f'Выберите товар категории \"{category["name"]}\"'
        buttons_data: List[Dict[str, Any]] = [
             {
                 'text': product['name'],
                 'action': {
                     'type': 'postback',
                     'payload': Callback.Schema().dumps({
                         'type': CallbackType.PRODUCT,
                         'id': product['id']
                     }),
                 }
             } for product in Product.objects.get_products(self.callback.id)][:10]
        print(buttons_data)
        self.data['inline_buttons'] = buttons_data

    def form_product_desc(self) -> None:
        """Формирует данные для описания выбранного товара с кнопкой 'Заказать'."""

        self.data['content_type'] = MessageContentType.INLINE
        product = Product.objects.get_product_by_id(self.callback.id)
        self.data['payload']['text'] = \
            f'Выбран товар \"{product["name"]}\"' \
            f'\n\nКраткое описание: {product["description"][:500]}' \
            f'\n\nСтоимость: {product["price"]}'
        buttons_data: List[Dict[str, Any]] = [
            {
                # 'text': f'Заказать поз. #{product["id"]}: {product["price"]}',
                'text': 'Заказать',
                'action': {
                    'type': 'postback',
                    'payload': Callback.Schema().dumps({
                        'type': CallbackType.ORDER,
                        'id': self.callback.id,
                    }),
                }
            }]
        print(buttons_data)
        self.data['inline_buttons'] = buttons_data

    def form_order_confirmation(self) -> None:
        """Формирует данные для сообщения с предложением выбрать платёжную систему для оплаты."""

        self.data['content_type'] = MessageContentType.INLINE
        product = Product.objects.get_product_by_id(self.callback.id)
        self.data['payload']['text'] = \
            f'Выбран товар \"{product["name"]}\"' \
            f'\n\nОплатить заказ за {product["price"]} через платёжную систему?'
        buttons_data: List[Dict[str, Any]] = [
            {
                # 'text': f'PayPal (поз. #{product["id"]}: {product["price"]})',
                'text': 'PayPal',
                'action': {
                    'type': 'postback',
                    'payload': Callback.Schema().dumps({
                        'type': CallbackType.PAYPAL,
                        'id': self.callback.id,
                    }),
                }
            },
            {
                # 'text': f'Stripe (поз. #{product["id"]}: {product["price"]})',
                'text': 'Stripe',
                'action': {
                    'type': 'postback',
                    'payload': Callback.Schema().dumps({
                        'type': CallbackType.STRIPE,
                        'id': self.callback.id,
                    }),
                }
            },
        ]
        print(buttons_data)
        self.data['inline_buttons'] = buttons_data

    def make_order(self) -> None:
        """Формирует заказ и готовит данные для сообщения со ссылкой для произведения оплаты пользователем."""

        self.data['content_type'] = MessageContentType.TEXT
        order = Order.objects.make_order(
            self.data['chat_id_in_messenger'],
            self.data['bot_id'],
            self.callback.id,
        )
        approve_link = ''
        if self.callback.type == CallbackType.PAYPAL:
            checkout_id = PaypalClient().check_out(order.pk, self.callback.id)
            approve_link = 'https://www.sandbox.paypal.com/checkoutnow?token=%s' % checkout_id
            checkout = Checkout.objects.make_checkout(PaymentSystems.PAYPAL.value, checkout_id, order.pk)
        elif self.callback.type == CallbackType.STRIPE:
            checkout_id = StripeClient().check_out(order.pk, self.callback.id)
            approve_link = '%s/billing/stripe_redirect/%s' % (SITE_URL, checkout_id)
            checkout = Checkout.objects.make_checkout(PaymentSystems.STRIPE.value, checkout_id, order.pk)
        self.data['payload']['text'] = f'Оплатите покупку по ссылке\n{approve_link}!'
