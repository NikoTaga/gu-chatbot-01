from collections import namedtuple
from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from clients.jivosite import JivositeClient
from clients.ok import OkClient
from entities import EventCommandReceived
from .handlers import message_handler


ChatEntry = namedtuple('ChatEntry', ['number', 'name', 'time'])
MessageEntry = namedtuple('MessageEntry', ['number', 'content', 'direction', 'time'])


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
    chats = [ChatEntry(i, f'chat number #{i}', datetime.now().date()) for i in range(20)]
    context = {
        'title_page': 'Список чатов',
        'objects_list': chats
    }

    return render(request, 'bot/chat_list.html', context)


def chat_view(request: HttpRequest, pk: int) -> HttpResponse:
    chats = [ChatEntry(
                       i,
                       f'chat number #{i}',
                       datetime.now().date(),
                       ) for i in range(20)]
    messages = [MessageEntry(
                             j,
                             f'Test message {pk}#{j}',
                             bool(j % 2),
                             datetime.now().date(),
                            ) for j in range(20)]
    context = {
        'title_page': 'Список чатов',
        'chat_list': chats,
        'message_list': messages,
        'selected': pk,
    }

    return render(request, 'bot/chat_view.html', context)
