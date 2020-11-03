from entities import EventCommandReceived, EventCommandToSend


def message_handler(event: EventCommandReceived) -> EventCommandToSend:
    """Обработчик входящего сообщения"""
    # преобразования полученного сообщения
    result = EventCommandToSend()
    return result
