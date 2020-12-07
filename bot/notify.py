from typing import TYPE_CHECKING

from builders import ECTSDirector
from clients.common import PlatformClientFactory
from constants import CallbackType

if TYPE_CHECKING:
    from billing.models import Checkout


def send_payment_completed(checkout: 'Checkout') -> None:
    """Формирует сообщение об удачной оплате и посылает его через соответствующий клиент."""

    bot_type = checkout.order.chat.bot.bot_type
    msg = ECTSDirector().create_message(
        callback_type=CallbackType.NOTIFY,
        bot_id=checkout.order.chat.bot.id,
        chat_id_in_messenger=checkout.order.chat.id_in_messenger,
        text=f'Оплата товара: {checkout.order.product.name} прошла успешно.\nСпасибо за покупку!',
    )
    client = PlatformClientFactory.create(bot_type)
    client.send_message(msg)
