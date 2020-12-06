from typing import Union, Dict, Any

from constants import BotType
from .ok import OkClient
from .jivosite import JivositeClient


# в принципе, не должно быть сложно объединить клиенты через абстракцию

class PlatformClientFactory:
    """Создаёт инстанс клиента социальной платформы по типу платформы."""

    types: Dict[int, Any] = {
        BotType.TYPE_JIVOSITE.value: JivositeClient,
        BotType.TYPE_OK.value: OkClient,
    }

    @classmethod
    def create(cls, bot_type: int) -> Union[OkClient, JivositeClient]:
        return cls.types[bot_type]()
