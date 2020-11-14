from typing import Dict, Any, List

from entities import EventCommandReceived, EventCommandToSend
from constants import *


def message_handler(event: EventCommandReceived) -> EventCommandToSend:
    """Обработчик входящего сообщения"""
    # преобразования полученного сообщения
    result = EventCommandToSend()
    return result


def test_handler(event: EventCommandReceived) -> EventCommandToSend:
    # начало формирования объекта с данными для ECR
    result_data: Dict[str, Any] = {
        'bot_id': event.bot_id,
        'chat_id_in_messenger': event.chat_id_in_messenger,
        'payload': {
            'direction': MessageDirection.SENT,
            'text': None,
        },
    }
    # в случае запроса номера категории
    if event.payload.command == '{"category": 1}':
        result_data['content_type'] = ContentType.TEXT
        result_data['payload']['text'] = 'Нажата кнопка "Category"!'
    # в случае запроса номера продукта
    elif event.payload.command == '{"product": 1}':
        result_data['content_type'] = ContentType.TEXT
        result_data['payload']['text'] = 'Нажата кнопка "Product"!'
    # в случае прихода текстового сообщения
    else:
        result_data['content_type'] = ContentType.INLINE
        result_data['payload']['text'] = 'Нажмите на кнопку!'
        buttons_data: List[Dict[str, Any]] = [
            {
                'text': 'Category',
                'action': {
                    'type': 'postback',
                    'payload': '{"category": 1}',
                }
            },
            {
                'text': 'Product',
                'action': {
                    'type': 'postback',
                    'payload': '{"product": 1}',
                }
            }
        ]
        result_data['inline_buttons'] = buttons_data

    result = EventCommandToSend.Schema().load(result_data)
    return result
