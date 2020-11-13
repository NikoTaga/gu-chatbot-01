import requests

from entities import EventCommandToSend
from .ok_constants import *
from .ok_entities import OutgoingMessage


class OkClient:
    """Класс для работы с Однокласниками"""
    token = 'tkn1wILRxmauO2rhrdYCdw41cqv2aLtebSzXqTHbv6SrRzQuZ7u8hz0ZOJMc9NmRESevE2:CLOKPPJGDIHBABABA'
    headers = {'Content-Type': 'application/json;charset=utf-8'}

    def send_message(self, payload: EventCommandToSend):
        """Отпрвка сообщения"""
        pass

    def send_test_message(self, payload: EventCommandToSend):
        msg_data = {
            'recipient': {
                'chat_id': payload.chat_id_in_messenger,
            },
            'message': {
                'text': payload.payload.text,
            }
        }
        if payload.inline_buttons:
            msg_data['message']['attachment'] = {
                'type': AttachmentType.INLINE_KEYBOARD,
                'payload': {
                    'keyboard': {
                        # это должно быть списком списков
                        # каждый список означает одну строку кнопок
                        'buttons': [[
                            {
                                'type': ButtonType.CALLBACK,
                                'text': entry.text,
                                'intent': ButtonIntent.POSITIVE,
                                'payload': entry.action.payload,
                            } for entry in payload.inline_buttons
                        ]]
                    }
                }
            }

        msg = OutgoingMessage.Schema().load(msg_data)

        send_link = f'https://api.ok.ru/graph/me/messages/{payload.chat_id_in_messenger}?access_token={self.token}'
        r = requests.post(send_link, headers=self.headers, data=msg.Schema().dumps(msg))
        print(r.text)
