from django.http import HttpRequest

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
