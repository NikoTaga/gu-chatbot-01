from datetime import datetime

import requests
from pprint import pprint
from typing import Dict, Any

from constants import CallbackType, MessageDirection, ChatType, MessageContentType
from entities import EventCommandToSend, EventCommandReceived, Callback, InlineButton
from clients.jivo_entities import JivoMessage, JivoEvent
from clients.jivo_constants import *


class JivositeClient:
    """Класс для работы с JivoSite"""
    token: str = 'test'
    headers: Dict[str, Any] = {'Content-Type': 'application/json'}
    command_cache: Dict[str, Dict[str, str]] = {}

    def form_jivo_event(self, payload: EventCommandToSend) -> JivoEvent:
        event_data: Dict[str, Any] = {
            'event': JivoEventType.BOT_MESSAGE,
            # todo think about how to work this around
            'id': str(payload.message_id),
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

        if payload.inline_buttons:
            self.command_cache[payload.chat_id_in_messenger] = {
                btn.text: btn.action.payload for btn in payload.inline_buttons
            }

        return event

    def parse_jivo_webhook(self, wh: JivoEvent) -> EventCommandReceived:
        # формирование объекта с данными для ECR
        ecr_data: Dict[str, Any] = {
            'bot_id': 2,
            # todo think about fixing
            'chat_id_in_messenger': wh.client_id,  # important, do not change
            'content_type': MessageContentType.COMMAND,
            'payload': {
                'direction': MessageDirection.RECEIVED,
                # todo CHECK DOES THIS EVEN WORK ??????
                'command': wh.message.button_id,  # it doesn't.
                'text': wh.message.text,
            },
            'chat_type': ChatType.PRIVATE,
            # switched places
            'user_id_in_messenger': str(wh.chat_id),
            'user_name_in_messenger': 'Тест',
            'message_id_in_messenger': str(wh.sender.id),
            'reply_id_in_messenger': None,
            'ts_in_messenger': str(datetime.fromtimestamp(int(wh.message.timestamp))),
        }

        try:
            if self.command_cache[wh.client_id]:
                ecr_data['payload']['command'] = self.command_cache[wh.client_id][wh.message.text]
        except KeyError as err:
            print(err.args)
        ecr = EventCommandReceived.Schema().load(ecr_data)

        return ecr

    def send_message(self, payload: EventCommandToSend):
        """Отпрвка сообщения"""
        pass

    def send_test_message(self, payload: EventCommandToSend) -> None:
        msg = self.form_jivo_event(payload)
        print('msg ====')
        pprint(msg)
        print()
        data = msg.Schema().dumps(msg)
        print('data ====')
        pprint(data)
        print()
        send_link = 'https://bot.jivosite.com/webhooks/ntDQ6AScFgYVtb8/test'
        r = requests.post(send_link, headers=self.headers, data=msg.Schema().dumps(msg))
        print(r)
        print(r.text)
        # url для отправки https://bot.jivosite.com/webhooks/ntDQ6AScFgYVtb8/test

