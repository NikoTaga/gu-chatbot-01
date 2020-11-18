from typing import Dict, Any, List

from marshmallow import ValidationError

from entities import EventCommandReceived, EventCommandToSend, Callback
from .dialog import Dialog
from .models import Message


def message_handler(event: EventCommandReceived) -> EventCommandToSend:
    """Обработчик входящего сообщения"""
    # преобразования полученного сообщения
    result = EventCommandToSend()
    return result


def test_handler(event: EventCommandReceived) -> EventCommandToSend:
    # -> сохранение сообщения и работа с юзером (Алекс)
    Message.objects.save_message(
        event.bot_id,
        event.user_id_in_messenger,
        event.user_name_in_messenger,
        event.chat_id_in_messenger,
        event.chat_type,
        event.payload.direction,
        event.content_type,
        str(event.payload.command),
        event.message_id_in_messenger
    )
    result_data: Dict[str, Any] = Dialog()(event)
    if result_data:
        Message.objects.save_message(
            result_data['bot_id'],
            event.user_id_in_messenger,
            event.user_name_in_messenger,
            result_data['chat_id_in_messenger'],
            event.chat_type,
            result_data['payload']['direction'],
            result_data['content_type'],
            result_data['payload']['text']
        )

    try:
        result = EventCommandToSend.Schema().load(result_data)
    except ValidationError as err:
        print(err.args)
    return result
