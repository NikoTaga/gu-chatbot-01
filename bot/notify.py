from typing import TYPE_CHECKING

from common.builders import MessageDirector
from common.constants import ChatType
from common.strings import NotifyPhrases
from .models import Message
from clients.common import PlatformClientFactory

if TYPE_CHECKING:
    from billing.models import Checkout


def send_payment_completed(checkout: 'Checkout') -> None:
    """Формирует сообщение об удачной оплате и посылает его через соответствующий клиент."""

    bot_type = checkout.order.chat.bot.bot_type
    command = MessageDirector().create_ects(
        bot_id=checkout.order.chat.bot.id,
        chat_id_in_messenger=checkout.order.chat.id_in_messenger,
        text=NotifyPhrases.PAYMENT_SUCCESS.value.format(name=checkout.order.product.name),
    )
    message = Message.objects.save_message(
        bot_id=command.bot_id,
        chat_id_in_messenger=command.chat_id_in_messenger,
        chat_type=ChatType.PRIVATE,
        message_direction=command.payload.direction,
        message_content_type=command.content_type,
        messenger_user_id=checkout.order.chat.bot_user.messenger_user_id,
        user_name=checkout.order.chat.bot_user.name,
        message_text=command.payload.text,
    )
    command.message_id = message.pk
    client = PlatformClientFactory.create(bot_type)
    client.send_message(command)
