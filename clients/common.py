from typing import Dict, Any, TYPE_CHECKING

from common.constants import BotType
from clients.ok.ok import OkClient
from clients.jivosite.jivosite import JivositeClient

if TYPE_CHECKING:
    from clients.abstract import SocialPlatformClient


class PlatformClientFactory:
    """Создаёт инстанс клиента социальной платформы по типу платформы."""

    types: Dict[int, Any] = {
        BotType.TYPE_JIVOSITE.value: JivositeClient,
        BotType.TYPE_OK.value: OkClient,
    }

    @classmethod
    def create(cls, bot_type: int) -> 'SocialPlatformClient':
        return cls.types[bot_type]()


# class SocialPlatformClient:
#
#     _token: str = ''
#     _headers: Dict[str, Any] = {'Content-Type': 'application/json'}
#     _command_cache: Dict[str, Dict[str, Optional[str]]] = {}
#     _send_link: str = ''
#
#     def __init__(self, bot_type):
#         self._bot_type: BotType = bot_type
#
#     def parse_incoming_webhook(self, wh: Dict[str, Any]) -> EventCommandReceived:
#         director = ECRDirectorFactory.create(self._bot_type)
#         ecr = director.create_ecr(wh)
#
#         return ecr
#
#     def _form_event_to_send(self, payload: EventCommandToSend) -> Dict[str, Any]:
#         director = EventDirectorFactory.create(self._bot_type)
#         event = director.create_event(payload)
#
#         return event.Schema().dump(event)
#
#     def _transfer(self, data: Dict[str, Any]) -> None:
#         r = requests.post(self._send_link, headers=self._headers, data=data)
#
#     def send_message(self, payload: EventCommandToSend) -> None:
#         msg_data = self._form_event_to_send(payload)
#         self._transfer(msg_data)
#
