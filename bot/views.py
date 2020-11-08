from datetime import datetime

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from typing import List, Dict, Any

from clients.jivosite import JivositeClient
from clients.ok import OkClient
from entities import EventCommandReceived
from .handlers import message_handler


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
            'name': f'chat number #{i}',
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
            'name': f'chat number #{i}',
            'time': datetime.now().date()
         } for i in range(20)
    ]
    messages: List[Dict[str, Any]] = [
        {
            'number': j,
            'content': f'Test message {pk}#{j}',
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
