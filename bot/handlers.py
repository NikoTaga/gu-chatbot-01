from typing import Dict, Any

from marshmallow import ValidationError

from entities import EventCommandReceived, EventCommandToSend
from .dialog import Dialog
from .models import Message


def message_handler(event: EventCommandReceived) -> EventCommandToSend:
    """Возвращает команду для отправки (ECTS) в ответ на принятую команду (ECR).

    Передаёт полученные данные обработчику логики диалога и сохраняет входящие/исходящие сообщения."""

    Message.objects.save_message(
        event.bot_id,
        event.user_id_in_messenger,
        event.user_name_in_messenger,
        event.chat_id_in_messenger,
        event.chat_type,
        event.payload.direction,
        event.content_type,
        str(event.payload.command),
        event.message_id_in_messenger)
    result: EventCommandToSend = Dialog().reply(event)
    if result:
        Message.objects.save_message(
            result.bot_id,
            event.user_id_in_messenger,
            event.user_name_in_messenger,
            result.chat_id_in_messenger,
            event.chat_type,
            result.payload.direction,
            result.content_type,
            result.payload.text,
        )

    try:
        result.Schema().validate(result)
    except ValidationError as err:
        print('Handler:', err.args)
    return result
