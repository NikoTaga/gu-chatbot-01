import requests
import logging
from typing import Dict, Any
from datetime import datetime

from bot.models import Bot
from builders import MessageDirector
from constants import MessageDirection, ChatType, MessageContentType, BotType
from entities import EventCommandToSend, EventCommandReceived
from .ok_constants import OK_TOKEN
from .ok_entities import OkOutgoingMessage, OkIncomingWebhook, OkAttachmentType, OkButtonType, OkButtonIntent


logger = logging.getLogger('clients')


class OkClient:
    """Клиент для работы с социальной платформой Одноклассники.

    Содержит методы для преобразования входящих вебхуков в формат ECR,
    формирования ECTS на основе сформированного ботом ответа
    и отправки сообщения в систему ОК.
    """

    headers: Dict[str, Any] = {'Content-Type': 'application/json;charset=utf-8'}

    @staticmethod
    def form_ok_message(payload: EventCommandToSend) -> OkOutgoingMessage:

        msg = MessageDirector().create_ok_message(payload)
        msg.Schema().validate(msg)

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

    def send_message(self, payload: EventCommandToSend) -> None:
        msg = self.form_ok_message(payload)

        send_link = 'https://api.ok.ru/graph/me/messages/{}?access_token={}'.format(
            payload.chat_id_in_messenger, OK_TOKEN
        )
        r = requests.post(send_link, headers=self.headers, data=msg.Schema().dumps(msg))
        logger.debug(f'OK answered: {r.text}')
