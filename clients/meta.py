from typing import Union

from constants import BotType
from .ok import OkClient
from .jivosite import JivositeClient


# в принципе, не должно быть сложно объединить клиенты через абстракцию

class PlatformClientFactory:
    types = {
        BotType.TYPE_JIVOSITE.value: JivositeClient,
        BotType.TYPE_OK.value: OkClient,
    }

    @classmethod
    def create(cls, bot_type: BotType) -> Union[OkClient, JivositeClient]:
        return cls.types[bot_type]()
