from typing import Dict, Any, List

from marshmallow import ValidationError

from entities import EventCommandReceived, EventCommandToSend, Callback
from constants import *
from .dialog import Dialog


def message_handler(event: EventCommandReceived) -> EventCommandToSend:
    """Обработчик входящего сообщения"""
    # преобразования полученного сообщения
    result = EventCommandToSend()
    return result


def test_handler(event: EventCommandReceived) -> EventCommandToSend:
    # -> сохранение сообщения и работа с юзером (Алекс)
    result_data: Dict[str, Any] = Dialog()(event)

    try:
        result = EventCommandToSend.Schema().load(result_data)
    except ValidationError as err:
        print(err.args)
    return result
