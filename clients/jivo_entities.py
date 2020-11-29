from dataclasses import field
from typing import ClassVar, List, Optional, Type

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from entities import SkipNoneSchema

from clients.jivo_constants import JivoMessageType, JivoEventType, JivoResponseType


@dataclass(order=True)
class JivoError:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    code: JivoResponseType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(JivoResponseType, by_value=True)
        }
    )
    message: Optional[str]


@dataclass(order=True, base_schema=SkipNoneSchema)
class JivoErrorMessage:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    error: JivoError


@dataclass(order=True)
class JivoButton:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    text: str
    id: int


@dataclass(order=True, base_schema=SkipNoneSchema)
class JivoMessage:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema
    
    type: JivoMessageType = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(JivoMessageType, by_value=True)
        }
    )
    text: Optional[str] = None
    timestamp: int = None
    button_id: Optional[str] = None
    title: str = None
    buttons: Optional[List[JivoButton]] = None



@dataclass(order=True, base_schema=SkipNoneSchema)
class JivoEvent:
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
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema
    
    id: int
    url: str
    
    
@dataclass(order=True)
class JivoIncomingWebhook:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    id: str
    site_id: str
    client_id: str
    chat_id: str
    sender: Optional[JivoSender]
    message: Optional[JivoMessage]
    event: JivoEventType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(JivoEventType, by_value=True)
        }
    )
