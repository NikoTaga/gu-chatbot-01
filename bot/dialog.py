from typing import Dict, Any, List, Callable
from json.decoder import JSONDecodeError

from billing.constants import PaymentSystems
from billing.stripe.client import StripeClient
from billing.paypal.client import PaypalClient
from constants import MessageDirection, MessageContentType, CallbackType, SITE_URL, BotType
from entities import EventCommandReceived, Callback, EventCommandToSend
from clients.ok import OkClient
from clients.jivosite import JivositeClient

from shop.models import Category, Product, Order
from billing.models import Checkout


class Dialog:

    def __call__(self, event: EventCommandReceived) -> Dict[str, Any]:
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
            self.callback: Callback = Callback.Schema().loads(command)
            variants[self.callback.type]()
        except (JSONDecodeError, KeyError, TypeError) as err:
            print(err.args)
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
        self.data['content_type'] = MessageContentType.INLINE
        self.data['payload']['text'] = 'Выберите категорию товара:'
        buttons_data: List[Dict[str, Any]] = [
            {
                'text': category['name'],
                'action': {
                    'type': 'postback',
                    'payload': Callback.Schema().dumps({
                        'type': CallbackType.CATEGORY,
                        'category': category['id']
                    }),
                }
            } for category in Category.objects.get_categories()][:10]
        print(buttons_data)
        self.data['inline_buttons'] = buttons_data

    def form_product_list(self) -> None:
        self.data['content_type'] = MessageContentType.INLINE
        category = Category.objects.get_category_by_id(self.callback.category)
        self.data['payload']['text'] = f'Выберите товар категории \"{category["name"]}\"'
        buttons_data: List[Dict[str, Any]] = [
             {
                 'text': product['name'],
                 'action': {
                     'type': 'postback',
                     'payload': Callback.Schema().dumps({
                         'type': CallbackType.PRODUCT,
                         'product': product['id']
                     }),
                 }
             } for product in Product.objects.get_products(self.callback.category)][:10]
        print(buttons_data)
        self.data['inline_buttons'] = buttons_data

    def form_product_desc(self) -> None:
        self.data['content_type'] = MessageContentType.INLINE
        product = Product.objects.get_product_by_id(self.callback.product)
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
                        'product': self.callback.product,
                    }),
                }
            }]
        print(buttons_data)
        self.data['inline_buttons'] = buttons_data

    def form_order_confirmation(self) -> None:
        self.data['content_type'] = MessageContentType.INLINE
        product = Product.objects.get_product_by_id(self.callback.product)
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
                        'product': self.callback.product,
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
                        'product': self.callback.product,
                    }),
                }
            },
        ]
        print(buttons_data)
        self.data['inline_buttons'] = buttons_data

    def make_order(self) -> None:
        self.data['content_type'] = MessageContentType.TEXT
        order = Order.objects.make_order(
            self.data['chat_id_in_messenger'],
            self.data['bot_id'],
            self.callback.product,
        )
        approve_link = ''
        if self.callback.type == CallbackType.PAYPAL:
            checkout_id = PaypalClient().check_out(order.pk, self.callback.product)
            approve_link = 'https://www.sandbox.paypal.com/checkoutnow?token=%s' % checkout_id
            checkout = Checkout.objects.make_checkout(PaymentSystems.PAYPAL.value, checkout_id, order.pk)
        elif self.callback.type == CallbackType.STRIPE:
            checkout_id = StripeClient().check_out(order.pk, self.callback.product)
            approve_link = '%s/billing/stripe_redirect/%s' % (SITE_URL, checkout_id)
            checkout = Checkout.objects.make_checkout(PaymentSystems.STRIPE.value, checkout_id, order.pk)
        self.data['payload']['text'] = f'Оплатите покупку по ссылке\n{approve_link}!'

    @staticmethod
    def send_paypal_payment_completed(checkout: Checkout) -> None:
        bot_type = checkout.order.chat.bot.bot_type
        msg = {
            'bot_id': checkout.order.chat.bot.id,
            'chat_id_in_messenger': checkout.order.chat.id_in_messenger,
            'content_type': MessageContentType.TEXT,
            'payload': {
                'direction': MessageDirection.SENT,
                'text': f'Оплата товара: {checkout.order.product.name} прошла успешно.\nСпасибо за покупку!',
            },
        }
        msg = EventCommandToSend.Schema().load(msg)
        if bot_type == BotType.TYPE_OK.value:
            OkClient().send_test_message(msg)
        elif bot_type == BotType.TYPE_JIVOSITE.value:
            JivositeClient().send_test_message(msg)
