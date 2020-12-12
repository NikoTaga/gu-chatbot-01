import requests
import logging
from datetime import datetime, timedelta
from ipaddress import ip_network, ip_address
from typing import Dict, Any, TYPE_CHECKING

from common.builders import MessageDirector
from bot.models import Bot, Message
from common.constants import MessageDirection, ChatType, MessageContentType, BotType
from common.entities import EventCommandToSend, EventCommandReceived
from .ok_constants import OK_TOKEN
from .ok_entities import OkOutgoingMessage, OkIncomingWebhook
from bot.apps import SingletonAPS
from clients.abstract import SocialPlatformClient
from clients.exceptions import OkServerError
from common.strings import OkStrings

if TYPE_CHECKING:
    from django.http import HttpRequest


logger = logging.getLogger('root')
bot_scheduler = SingletonAPS().get_aps


class OkClient(SocialPlatformClient):
    """Клиент для работы с социальной платформой Одноклассники.

    Содержит методы для преобразования входящих вебхуков в формат ECR,
    формирования ECTS на основе сформированного ботом ответа
    и отправки сообщения в систему ОК.
    """

    headers: Dict[str, Any] = {'Content-Type': 'application/json;charset=utf-8'}

    @staticmethod
    def verify_request(request: 'HttpRequest') -> bool:
        ip_pool = [ip_network(net)
                   for net in OkStrings.IP_POOL.value.split(', ')]
        # todo might not work due to host routing
        logger.info(f'request.META: {request.META}')
        host_ip = ip_address(request.META.get('HTTP_X_FORWARDED_FOR').split(', ')[0])

        for network in ip_pool:
            if host_ip in network:
                return True
        return False

    def _form_message(self, payload: EventCommandToSend) -> OkOutgoingMessage:

        msg = MessageDirector().create_ok_message(payload)
        msg.Schema().validate(msg.Schema().dump(msg))

        logger.debug(msg)

        return msg

    def parse_webhook(self, request: 'HttpRequest') -> EventCommandReceived:
        wh = OkIncomingWebhook.Schema().loads(request.body)
        logger.debug(wh)
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
        # logger.debug(ecr)

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
        msg = self._form_message(payload)

        send_link = OkStrings.API_LINK.value.format(
            chat_id=payload.chat_id_in_messenger, token=OK_TOKEN
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
