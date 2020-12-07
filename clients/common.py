from typing import Union, Dict, Any, Optional

from constants import BotType
from clients.ok.ok import OkClient
from clients.jivosite.jivosite import JivositeClient

# в принципе, не должно быть сложно объединить клиенты через абстракцию
from entities import EventCommandReceived, EventCommandToSend


class PlatformClientFactory:
    """Создаёт инстанс клиента социальной платформы по типу платформы."""

    types: Dict[int, Any] = {
        BotType.TYPE_JIVOSITE.value: JivositeClient,
        BotType.TYPE_OK.value: OkClient,
    }

    @classmethod
    def create(cls, bot_type: int) -> Union[OkClient, JivositeClient]:
        return cls.types[bot_type]()
