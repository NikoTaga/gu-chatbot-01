from typing import Dict, Any, List, Callable, Optional
from json.decoder import JSONDecodeError
import logging

from billing.common import PaymentClientFactory
from builders import MessageDirector
from constants import CallbackType
from entities import EventCommandReceived, Callback, EventCommandToSend

from shop.models import Category, Product, Order


logger = logging.getLogger('bot')


class Dialog:
    """Содержит логику взаимодействия бота с пользователем.

    Осуществляет диалог из нескольких этапов, предлагая выбрать категорию, товар, систему оплаты.
    По итогу инициирует выставление счёта в соответствующей системе."""

    callback: Callback

    def reply(self, event: EventCommandReceived) -> Optional[EventCommandToSend]:
        """Основной метод класса, формирует словарь-ответ на базе типа и параметров запроса в формате ECR."""

        variants: Dict[CallbackType, Callable[[EventCommandReceived], EventCommandToSend]] = {
            CallbackType.GREETING: self.form_category_list,
            CallbackType.CATEGORY: self.form_product_list,
            CallbackType.PRODUCT: self.form_product_desc,
            CallbackType.ORDER: self.form_order_confirmation,
            CallbackType.PAYPAL: self.make_order,
            CallbackType.STRIPE: self.make_order,
        }

        result = None
        if event.payload.command is not None:
            command: str = event.payload.command
            try:
                self.callback = Callback.Schema().loads(command)
                result = variants[self.callback.type](event)
            except JSONDecodeError as err:
                logger.error(f'Dialog GREETING formed: {err.args}')
                result = self._form_greeting(event)
            except KeyError as err:
                logger.debug(f'Dialog.ready(): {err.args}')
                # result = self.form_category_list(event)
        else:
            logger.debug('Dialog GREETING formed.')
            result = self._form_greeting(event)

        return result

    def _form_greeting(self, event: EventCommandReceived) -> EventCommandToSend:
        """Формирует приветствие пользователя при написании произвольного сообщения."""

        button_data: List[Dict[str, Any]] = [
            {
                'title': 'Начать работу',
                'id': 0,
                'type': CallbackType.GREETING,
            }]

        greeting = 'Добро пожаловать{}!\nНажмите на кнопку для начала работы:'
        if event.user_name_in_messenger:
            greeting = greeting.format(f', {event.user_name_in_messenger}')
        else:
            greeting = greeting.format('')

        msg = MessageDirector().create_ects(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text=greeting,
            button_data=button_data,
        )

        logger.debug(f'"BUTTONS: {button_data}"')

        return msg

    def form_category_list(self, event: EventCommandReceived) -> EventCommandToSend:
        """Собирает список категорий в виде данных для сообщения с соответствующими кнопками."""

        button_data: List[Dict[str, Any]] = [
            {
                'title': category['name'],
                'id': category['id'],
                'type': CallbackType.CATEGORY,
            } for category in Category.objects.get_categories()][:10]

        msg = MessageDirector().create_ects(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text='Выберите категорию товара:',
            button_data=button_data,
        )

        logger.debug(f'"BUTTONS: {button_data}"')

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

        msg = MessageDirector().create_ects(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text='Выберите товар категории "{}"'.format(category['name']),
            button_data=button_data,
        )

        logger.debug(f'"BUTTONS: {button_data}"')

        return msg

    def form_product_desc(self, event: EventCommandReceived) -> EventCommandToSend:
        """Формирует данные для описания выбранного товара с кнопкой 'Заказать'."""

        product = Product.objects.get_product_by_id(self.callback.id)
        text = 'Выбран товар "{}"\n\nКраткое описание: {}\n\nСтоимость: {}'.format(
            product['name'], product['description'][:400], product['price']
        )
        button_data: List[Dict[str, Any]] = [
            {
                'title': 'Заказать',
                'id': self.callback.id,
                'type': CallbackType.ORDER,
            }]

        msg = MessageDirector().create_ects(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text=text,
            button_data=button_data,
        )

        logger.debug(f'"BUTTONS: {button_data}"')

        return msg

    def form_order_confirmation(self, event: EventCommandReceived) -> EventCommandToSend:
        """Формирует данные для сообщения с предложением выбрать платёжную систему для оплаты."""

        product = Product.objects.get_product_by_id(self.callback.id)
        text = 'Выбран товар \"{}\"' \
               '\n\nОплатить заказ за {} через платёжную систему?'.format(
                product["name"], product["price"]
                )
        # todo где-то нужна метаинформация по списку систем
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

        msg = MessageDirector().create_ects(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text=text,
            button_data=button_data,
        )

        logger.debug(f'"BUTTONS: {button_data}"')

        return msg

    def make_order(self, event: EventCommandReceived) -> EventCommandToSend:
        """Формирует заказ и готовит данные для сообщения со ссылкой для произведения оплаты пользователем."""

        order = Order.objects.make_order(
            event.chat_id_in_messenger,
            event.bot_id,
            self.callback.id,
        )
        payment_client = PaymentClientFactory.create(self.callback.type.value)
        approve_link = payment_client.check_out(order.pk, self.callback.id)

        text = 'Оплатите покупку по ссылке\n{}!'.format(approve_link)

        msg = MessageDirector().create_ects(
            bot_id=event.bot_id,
            chat_id_in_messenger=event.chat_id_in_messenger,
            text=text,
        )

        return msg
