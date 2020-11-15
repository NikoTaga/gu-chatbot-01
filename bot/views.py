from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
# чтобы разрешить кросс-сайт POST запросы
from django.views.decorators.csrf import csrf_exempt
from typing import List, Dict, Any

from clients.jivosite import JivositeClient
from clients.ok import OkClient
from constants import *
from entities import EventCommandReceived, EventCommandToSend
from .handlers import message_handler, test_handler

from clients.ok_entities import OkIncomingWebhook


@csrf_exempt
def ok_test_webhook(request: HttpRequest) -> HttpResponse:
    client = OkClient()

    # Запросы могут производиться только с определенного списка IP-адресов:
    #
    # 217.20.145.192/28
    # 217.20.151.160/28
    # 217.20.153.48/28
    # но с ngrok хосты расшифровываются как его удалённый хост
    print('host: ', request.get_host())
    wh = OkIncomingWebhook.Schema().loads(request.body)
    print(wh)
    event: EventCommandReceived = client.parse_ok_webhook(wh)
    result: EventCommandToSend = test_handler(event)
    client.send_test_message(result)

    # скрипт обязательно должен подтверждать получение с помощью отправки 200 ОК
    return HttpResponse('OK')


def ok_webhook(request: HttpRequest) -> None:
    client = OkClient()
    event = EventCommandReceived()
    result = message_handler(event)
    client.send_message(result)


def jivosite_webhook(request: HttpRequest) -> None:
    client = JivositeClient()
    event = EventCommandReceived()
    result = message_handler(event)
    client.send_message(result)


def chat_list(request: HttpRequest) -> HttpResponse:
    chats: List[Dict[str, Any]] = [
        {
            'number': i,
            'name': f'chat number {"f"*100} #{i}',
            'time': datetime.now().date()
        } for i in range(20)
    ]
    context: Dict[str, Any] = {
        'title_page': 'Список чатов',
        'objects_list': chats
    }

    return render(request, 'bot/chat_list.html', context)


def chat_view(request: HttpRequest, pk: int) -> HttpResponse:
    chats: List[Dict[str, Any]] = [
        {
            'number': i,
            'name': f'chat numberf  {"f"*100}  #{i}',
            'time': datetime.now().date()
         } for i in range(20)
    ]
    messages: List[Dict[str, Any]] = [
        {
            'number': j,
            'content': f'Test message {"f"*100} {pk}#{j}',
            'direction': bool(j % 2),
            'time': datetime.now().strftime('%H:%M %d-%m-%Y'),
        } for j in range(20)
    ]
    context: Dict[str, Any] = {
        'title_page': 'Список чатов',
        'chat_list': chats,
        'message_list': messages,
        'selected': pk,
    }

    return render(request, 'bot/chat_view.html', context)
