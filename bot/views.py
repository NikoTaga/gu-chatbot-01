from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
# чтобы разрешить кросс-сайт POST запросы
from django.views.decorators.csrf import csrf_exempt
from typing import List, Dict, Any, Optional
from marshmallow.exceptions import ValidationError
import logging

from common.constants import BotType
from common.entities import EventCommandReceived, EventCommandToSend
from .handlers import message_handler
from clients.common import PlatformClientFactory
from .models import Chat, Message


logger = logging.getLogger('root')


@csrf_exempt  # type: ignore
def ok_webhook(request: HttpRequest) -> HttpResponse:
    """Обрабатывает входящие вебхуки со стороны OK и возвращает 200 ОК.

    Проводит верификацию хоста (?), проводит парсинг в ECR,
    направляет в хендлер для получения ответа и отсылает обратно клиенту при удаче."""

    client = PlatformClientFactory.create(BotType.TYPE_OK.value)

    logger.debug(f'"inc wh from: {request.get_host()}')
    # todo doesn't work yet due to ngrok
    logger.debug(f'verified: {client.verify_request(request)}')
    try:
        event: EventCommandReceived = client.parse_webhook(request)
        logger.debug(event)
        result: Optional[EventCommandToSend] = message_handler(event)
        if result is not None:
            client.send_message(result)
    except ValidationError as e:
        logger.error(f'OK webhook: {e.args}')

    # скрипт обязательно должен подтверждать получение с помощью отправки 200 ОК
    return HttpResponse('OK')


@csrf_exempt  # type: ignore
def jivo_webhook(request: HttpRequest) -> HttpResponse:
    """Обрабатывает входящие вебхуки со стороны JivoSite и возвращает 200 ОК.

    Проводит парсинг в ECR, направляет в хендлер для получения ответа и отсылает обратно клиенту при удаче."""

    logger.debug(f'"inc jivo wh from: {request.get_host()}')
    client = PlatformClientFactory.create(BotType.TYPE_JIVOSITE.value)
    try:
        event: EventCommandReceived = client.parse_webhook(request)
        logger.debug(event)
        result: Optional[EventCommandToSend] = message_handler(event)
        if result is not None:
            client.send_message(result)
    except ValidationError as e:
        logger.error(f'JIVO webhook: {e.args}')

    return HttpResponse('OK')


def chat_view(request: HttpRequest, pk: Optional[int] = None) -> HttpResponse:
    """Отображает список проведённых чатов и содержимое просматриваемого чата."""

    chats: List[Dict[str, Any]] = [
        {
            'number': chat.pk,
            'name': chat.bot_user.name,
            'chat_last_message': chat.last_message_text,
            'time': chat.last_message_time
        } for chat in Chat.objects.all()
    ]
    messages: List[Dict[str, Any]] = []
    if pk:
        messages = [
            {
                'number': message.pk,
                'content': message.text,
                'direction': bool(message.direction % 2),
                'time': message.created_at,
            } for message in Message.objects.get_chat_messages(pk)
        ]
    context: Dict[str, Any] = {
        'title_page': 'Список чатов',
        'chat_list': chats,
        'message_list': messages,
        'selected': pk,
    }

    return render(request, 'bot/chat_view.html', context)
