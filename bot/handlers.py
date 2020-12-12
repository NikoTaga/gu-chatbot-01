import logging
from typing import Optional

from marshmallow import ValidationError

from common.entities import EventCommandReceived, EventCommandToSend
from .dialog import Dialog
from .models import Message


logger = logging.getLogger('root')


def message_handler(event: EventCommandReceived) -> Optional[EventCommandToSend]:
    """Возвращает команду для отправки (ECTS) в ответ на принятую команду (ECR).

    Передаёт полученные данные обработчику логики диалога и сохраняет входящие/исходящие сообщения."""

    Message.objects.save_message(
        event.bot_id,
        event.chat_id_in_messenger,
        event.chat_type,
        event.payload.direction,
        event.content_type,
        event.user_id_in_messenger,
        event.user_name_in_messenger,
        str(event.payload.command),
        event.message_id_in_messenger)
    result: Optional[EventCommandToSend] = Dialog().reply(event)
    if result:
        message = Message.objects.save_message(
            result.bot_id,
            result.chat_id_in_messenger,
            event.chat_type,
            result.payload.direction,
            result.content_type,
            event.user_id_in_messenger,
            event.user_name_in_messenger,
            result.payload.text,
        )
        result.message_id = message.pk
        try:
            result.Schema().validate(result.Schema().dump(result))
        except ValidationError as err:
            logger.error(f'Malformed ECTS in handler: {err.args}')
    return result
