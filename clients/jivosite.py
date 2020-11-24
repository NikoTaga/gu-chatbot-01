from datetime import datetime

import requests
from typing import Dict, Any

from constants import ContentType, MessageDirection, ChatType, MessageContentType
from entities import EventCommandToSend, EventCommandReceived
from clients.jivo_entities import JivoMessage, JivoEvent
from clients.jivo_constants import *


class JivositeClient:
    """Класс для работы с JivoSite"""
    token: str
    headers: Dict[str, Any] = {'Content-Type': 'application/json;charset=utf-8'}
    button_commands: Dict[int, str] = {
        0: '{"category": 1}',
        1: '{"product": 1}'
    }

    @staticmethod
    def form_jivo_event(payload: EventCommandToSend) -> JivoEvent:
        event_data: Dict[str, Any] = {
            'event': JivoEventType.BOT_MESSAGE,
            # todo think about how to work this around
            'id': payload.message_id,
            'client_id': payload.chat_id_in_messenger,
        }
        msg_data: Dict[str, Any] = {
            'text': payload.payload.text,
            'timestamp': datetime.now().timestamp()
        }
        if payload.inline_buttons:
            msg_data['title'] = payload.payload.text
            msg_data['type'] = JivoMessageType.BUTTONS
            msg_data['buttons'] = [
                {
                    'text': payload.inline_buttons[i].text,
                    'id': i,
                } for i in range(len(payload.inline_buttons))]
        else:
            msg_data['type'] = JivoMessageType.TEXT
        event_data['message'] = msg_data

        event = JivoEvent.Schema().load(event_data)

        return event

    @staticmethod
    def parse_jivo_webhook(wh: JivoEvent) -> EventCommandReceived:
        # формирование объекта с данными для ECR
        ecr_data: Dict[str, Any] = {
            'bot_id': 1,
            # todo think about fixing
            'chat_id_in_messenger': wh.chat_id,
            'content_type': MessageContentType.COMMAND,
            'payload': {
                'direction': MessageDirection.RECEIVED,
                # todo CHECK DOES THIS EVEN WORK ??????
                'command': wh.message.button_id,
            },
            'chat_type': ChatType.PRIVATE,
            # switched places
            'user_id_in_messenger': wh.chat_id
        }
        ecr = EventCommandReceived.Schema().load(ecr_data)
        return ecr

    def send_message(self, payload: EventCommandToSend):
        """Отпрвка сообщения"""
        pass

    def send_test_message(self, payload: EventCommandToSend) -> None:
        msg = self.form_jivo_event(payload)

        send_link = f'{payload.chat_id_in_messenger}{self.token}'
        r = requests.post(send_link, headers=self.headers, data=msg.Schema().dumps(msg))
        print(r.text)
