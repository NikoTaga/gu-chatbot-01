from dataclasses import field
from typing import ClassVar, List, Optional, Type

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from .jivo_constants import *
from .ok_entities import SkipNoneSchema


@dataclass(order=True)
class JivoError:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    code: ResponseType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(ResponseType, by_value=True)
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
    id: str


@dataclass(order=True, base_schema=SkipNoneSchema)
class JivoMessage:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    type: JivoMessageType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(JivoMessageType, by_value=True)
        }
    )
    text: str
    timestamp: int
    button_id: Optional[int]
    title: Optional[str]
    content: Optional[str]
    buttons: Optional[List[JivoButton]] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow.fields.Nested(JivoButton.Schema()),
                allow_none=True,
                validate=marshmallow.validate.Length(max=3),
            )
        }
    )


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