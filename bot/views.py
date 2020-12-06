from pprint import pprint
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
# чтобы разрешить кросс-сайт POST запросы
from django.views.decorators.csrf import csrf_exempt
from typing import List, Dict, Any
from marshmallow.exceptions import ValidationError

from constants import BotType
from entities import EventCommandReceived, EventCommandToSend
from .handlers import message_handler
from clients.common import PlatformClientFactory
from clients.ok_entities import OkIncomingWebhook
from clients.jivo_entities import JivoIncomingWebhook
from .models import Chat, Message


@csrf_exempt  # type: ignore
def ok_webhook(request: HttpRequest) -> HttpResponse:
    """Обрабатывает входящие вебхуки со стороны OK и возвращает 200 ОК.

    Проводит верификацию хоста (?), проводит парсинг в ECR,
    направляет в хендлер для получения ответа и отсылает обратно клиенту при удаче."""

    client = PlatformClientFactory.create(BotType.TYPE_OK.value)

    # Запросы могут производиться только с определенного списка IP-адресов:
    #
    # 217.20.145.192/28
    # 217.20.151.160/28
    # 217.20.153.48/28
    # но с ngrok хосты расшифровываются как его удалённый хост
    print('host: ', request.get_host())
    try:
        wh = OkIncomingWebhook.Schema().loads(request.body)
        print(wh)
        event: EventCommandReceived = client.parse_ok_webhook(wh)
        result: EventCommandToSend = message_handler(event)
        client.send_message(result)
    except ValidationError as e:
        print(e.args)

    # скрипт обязательно должен подтверждать получение с помощью отправки 200 ОК
    return HttpResponse('OK')


@csrf_exempt  # type: ignore
def jivo_webhook(request: HttpRequest) -> HttpResponse:
    """Обрабатывает входящие вебхуки со стороны JivoSite и возвращает 200 ОК.

    Проводит парсинг в ECR, направляет в хендлер для получения ответа и отсылает обратно клиенту при удаче."""

    print(request.body)
    client = PlatformClientFactory.create(BotType.TYPE_JIVOSITE.value)
    try:
        wh = JivoIncomingWebhook.Schema().loads(request.body)
        print('wh ===')
        print(wh)
        print()
        event: EventCommandReceived = client.parse_jivo_webhook(wh)
        print('event ===')
        pprint(event)
        print()
        result: EventCommandToSend = message_handler(event)
        print('result ===')
        pprint(result)
        print()
        client.send_message(result)
    except ValidationError as e:
        print(e.args)

    return HttpResponse('OK')


def chat_list(request: HttpRequest) -> HttpResponse:
    """Отображает список проведённых чатов.

    Сообщает имя клиента, последнее сообщение и время его отправки.
    Позволяет открыть требуемый чат для просмотра содержимого."""

    chats: List[Dict[str, Any]] = [
        {
            'number': chat.pk,
            'name': chat.bot_user.name,
            'chat_last_message': chat.last_message_text,
            'time': chat.last_message_time,
        } for chat in Chat.objects.all()
    ]
    context: Dict[str, Any] = {
        'title_page': 'Список чатов',
        'objects_list': chats
    }

    return render(request, 'bot/chat_list.html', context)


# todo well that's some hardcore duplication
def chat_view(request: HttpRequest, pk: int) -> HttpResponse:
    """Отображает список проведённых чатов и содержимое просматриваемого чата."""

    chats: List[Dict[str, Any]] = [
        {
            'number': chat.pk,
            'name': chat.bot_user.name,
            'chat_last_message': chat.last_message_text,
            'time': chat.last_message_time
        } for chat in Chat.objects.all()
    ]
    messages: List[Dict[str, Any]] = [
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
