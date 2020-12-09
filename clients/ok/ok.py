import requests
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from bot.models import Bot, Message
from constants import MessageDirection, ChatType, MessageContentType, BotType
from entities import EventCommandToSend, EventCommandReceived
from .ok_constants import OK_TOKEN
from .ok_entities import OkOutgoingMessage, OkIncomingWebhook, OkAttachmentType, OkButtonType, OkButtonIntent
from bot.apps import SingletonAPS
from ..exceptions import OkServerError

logger = logging.getLogger('clients')
bot_scheduler = SingletonAPS().get_aps


class OkClient:
    """Клиент для работы с социальной платформой Одноклассники.

    Содержит методы для преобразования входящих вебхуков в формат ECR,
    формирования ECTS на основе сформированного ботом ответа
    и отправки сообщения в систему ОК.
    """

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
            msg_data['message']['attachment'] = {
                'type': OkAttachmentType.INLINE_KEYBOARD,
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
                            }
                        ] for entry in payload.inline_buttons]
                    }
                }
            }

        msg = OkOutgoingMessage.Schema().load(msg_data)

        logger.debug(msg)

        return msg

    @staticmethod
    def parse_ok_webhook(wh: OkIncomingWebhook) -> EventCommandReceived:
        # формирование объекта с данными для ECR
        ecr_data: Dict[str, Any] = {
            'bot_id': Bot.objects.get_bot_id_by_type(BotType.TYPE_OK.value),
            'chat_id_in_messenger': wh.recipient.chat_id,
            'content_type': MessageContentType.COMMAND,
            'payload': {
                'direction': MessageDirection.RECEIVED,
                'command': wh.payload,
                'text': wh.message.text if wh.message else None,
            },
            'chat_type': ChatType.PRIVATE,
            'user_id_in_messenger': wh.sender.user_id,
            'user_name_in_messenger': wh.sender.name,
            'message_id_in_messenger': wh.mid if wh.mid else wh.message.mid,
            'reply_id_in_messenger': wh.message.reply_to if wh.message else None,
            'ts_in_messenger': str(datetime.fromtimestamp(wh.timestamp // 1000)),
        }
        ecr = EventCommandReceived.Schema().load(ecr_data)
        logger.debug(ecr)

        return ecr

    def _post_to_platform(self, message_id: int, send_link: str, data: str) -> None:
        print('Trying to send...')
        try:
            r = requests.post(send_link, headers=self.headers, data=data)
            logger.debug(f'OK answered: {r.text}')
            bot_scheduler.remove_job(f'ok_{message_id}')
            if 'invocation-error' in r.headers:
                logger.error(f'OK error: {r.headers["invocation-error"]} -> {r.json()}')
                raise OkServerError(r.headers["invocation-error"], r.json())
            Message.objects.set_sent(message_id)
        except (requests.Timeout, requests.ConnectionError) as e:
            logger.error(f'OK unreachable: {e.args}')

    def send_message(self, payload: EventCommandToSend) -> None:
        msg = self.form_ok_message(payload)

        send_link = 'https://api.ok.ru/graph/me/messages/{}?access_token={}'.format(
            payload.chat_id_in_messenger, OK_TOKEN
        )

        data = msg.Schema().dumps(msg)
        logger.debug(f'Sending to OK: {data}')

        bot_scheduler.add_job(
            self._post_to_platform,
            'interval',
            seconds=5,
            next_run_time=datetime.now(),
            end_date=datetime.now() + timedelta(minutes=5),
            args=[payload.message_id, send_link, data],
            id=f'ok_{payload.message_id}',
            )
