import requests
from typing import Dict, Any

from constants import ContentType, MessageDirection, ChatType
from entities import EventCommandToSend, EventCommandReceived
from .ok_constants import *
from .ok_entities import OkOutgoingMessage, OkIncomingWebhook


class OkClient:
    """Класс для работы с Однокласниками"""
    token: str = 'tkn1wILRxmauO2rhrdYCdw41cqv2aLtebSzXqTHbv6SrRzQuZ7u8hz0ZOJMc9NmRESevE2:CLOKPPJGDIHBABABA'
    headers: Dict[str, Any] = {'Content-Type': 'application/json;charset=utf-8'}

    @staticmethod
    def form_ok_message(payload: EventCommandToSend) -> OkOutgoingMessage:
        msg_data: Dict[str, Any] = {
            'recipient': {
                'chat_id': payload.chat_id_in_messenger,
            },
            'message': {
                'text': payload.payload.text,
            }
        }
        if payload.inline_buttons:
            msg_data['message']['attachment']: Dict[str, Any] = {
                'type': AttachmentType.INLINE_KEYBOARD,
                'payload': {
                    'keyboard': {
                        # это должно быть списком списков
                        # каждый список означает одну строку кнопок
                        'buttons': [[
                            {
                                'type': OkButtonType.CALLBACK,
                                'text': entry.text,
                                'intent': OkButtonIntent.POSITIVE,
                                'payload': entry.action.payload,
                            } for entry in payload.inline_buttons
                        ]]
                    }
                }
            }

        msg = OkOutgoingMessage.Schema().load(msg_data)

        return msg

    @staticmethod
    def parse_ok_webhook(wh: OkIncomingWebhook) -> EventCommandReceived:
        # формирование объекта с данными для ECR
        ecr_data: Dict[str, Any] = {
            'bot_id': 0,
            'chat_id_in_messenger': wh.recipient.chat_id,
            'content_type': ContentType.COMMAND,
            'payload': {
                'direction': MessageDirection.RECEIVED,
                'command': wh.payload,
            },
            'chat_type': ChatType.PRIVATE,
            'user_id_in_messenger': wh.sender.user_id
        }
        ecr = EventCommandReceived.Schema().load(ecr_data)
        print(ecr)
        return ecr

    def send_message(self, payload: EventCommandToSend):
        """Отпрвка сообщения"""
        pass

    def send_test_message(self, payload: EventCommandToSend) -> None:
        msg = self.form_ok_message(payload)

        send_link = f'https://api.ok.ru/graph/me/messages/{payload.chat_id_in_messenger}?access_token={self.token}'
        r = requests.post(send_link, headers=self.headers, data=msg.Schema().dumps(msg))
        print(r.text)
