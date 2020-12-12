"""Содержит сущности для сериализации данных при обмене с JivoSite."""

from dataclasses import field
from typing import ClassVar, List, Optional, Type

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from common.entities import SkipNoneSchema

from clients.jivosite.jivo_constants import JivoMessageType, JivoEventType, JivoResponseType


@dataclass(order=True)
class JivoError:
    """Класс данных для хранения информации об ошибке работы с JIVO.

    Включает код и описание ошибки."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    code: JivoResponseType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(JivoResponseType, by_value=True)
        }
    )
    message: Optional[str]


@dataclass(order=True, base_schema=SkipNoneSchema)
class JivoErrorMessage:
    """Класс данных для обёртывания информации об ошибке Jivo."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    error: JivoError


@dataclass(order=True)
class JivoButton:
    """Класс данных для хранения информации о кнопке в сообщении."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    text: str
    id: int


@dataclass(order=True, base_schema=SkipNoneSchema)
class JivoMessage:
    """Класс данных для хранения информации о сообщении в системе JivoSite.

    Содержит тип, текст, таймстамп, id нажатой кнопки (не используется), заголовок и кнопки.
    """

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    timestamp: int
    type: JivoMessageType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(JivoMessageType, by_value=True)
        }
    )
    text: str
    title: Optional[str] = None
    button_id: Optional[str] = None
    buttons: Optional[List[JivoButton]] = None


@dataclass(order=True, base_schema=SkipNoneSchema)
class JivoEvent:
    """Класс данных для хранения информации об исходящем сообщении JivoSite.

    Содержит тип, идентификатор сообщения, информацию о чате и клиенте Jivo, а также тело сообщения.
    """

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    event: JivoEventType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(JivoEventType, by_value=True)
        }
    )
    id: str
    client_id: str
    chat_id: Optional[str]
    message: Optional[JivoMessage]


@dataclass(order=True, base_schema=SkipNoneSchema)
class JivoSender:
    """Класс данных для хранения информации о отправителе входящего сообщения Jivo."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    id: int
    url: str


@dataclass(order=True)
class JivoIncomingWebhook:
    """Класс данных для хранения информации о входящем вебхуке от JivoSite."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    id: str
    client_id: str
    chat_id: str
    site_id: Optional[str]
    sender: Optional[JivoSender]
    message: Optional[JivoMessage]
    event: JivoEventType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(JivoEventType, by_value=True)
        }
    )
