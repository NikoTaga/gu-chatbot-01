from abc import ABC
from dataclasses import field
from datetime import datetime
from typing import (ClassVar, List, Optional, Type, Dict, Any)

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from common.constants import (ChatType, GenericTemplateActionType, MessageDirection, CallbackType,
                              MessageContentType)


class LinterFix:

    # todo rework this
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)  # type: ignore


# заставляет отбрасывать все значения None при дампе
# имеет смысл промаркировать все классы, данные из которых планируются к передаче НА удалённый сервер
class SkipNoneSchema(marshmallow.Schema):
    @marshmallow.post_dump  # type: ignore
    def remove_none_values(self, data: Dict[Any, Any], **kwargs: Dict[str, Any]) -> Dict[Any, Any]:
        return {
            key: value for key, value in data.items()
            if value is not None
        }


@dataclass(order=True)
class Contact:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_id: Optional[int] = None


@dataclass(order=True)
class GenericTemplateAction(LinterFix):
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    type: GenericTemplateActionType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(GenericTemplateActionType, by_value=True)
        }
    )
    link: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    payload: Optional[str] = field(
        default=None,
        compare=False,
        metadata={
            "marshmallow_field": marshmallow.fields.String(
                allow_none=True,
                validate=marshmallow.validate.Length(max=64),
            )
        }
    )


@dataclass(order=True)
class InlineButton(LinterFix):
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    text: str
    action: GenericTemplateAction


@dataclass(order=True)
class GenericTemplate:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    title: str
    description: Optional[str] = None
    image_url: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    action: Optional[GenericTemplateAction] = None
    buttons: Optional[List[InlineButton]] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow.fields.Nested(InlineButton.Schema()),
                allow_none=True,
                validate=marshmallow.validate.Length(max=3),
            )
        }
    )
    json_data: Optional[dict] = None  # type: ignore


@dataclass(order=True)
class Payload:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    direction: MessageDirection = field(
        default=MessageDirection.RECEIVED,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(MessageDirection, by_value=True)
        }
    )
    text: Optional[str] = None
    contact: Optional[Contact] = None
    image_url: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    file_url: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    video_url: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    inline: Optional[InlineButton] = None
    command: Optional[str] = None
    voice: Optional[bytes] = None
    carousel: Optional[List[GenericTemplate]] = None


@dataclass(order=True)
class AbstractCommand(ABC):
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    bot_id: int
    chat_id_in_messenger: str
    content_type: MessageContentType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(MessageContentType, by_value=True)
        }
    )
    payload: Payload


@dataclass(order=True)
class EventCommandReceived(LinterFix, AbstractCommand):
    chat_type: ChatType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(ChatType, by_value=True)
        }
    )
    user_id_in_messenger: Optional[str]
    is_redirect: bool = False  # TODO: Legacy - удалить
    bot_user_id: Optional[int] = None
    message_id_in_messenger: Optional[str] = None
    reply_id_in_messenger: Optional[str] = None
    chat_avatar_in_messenger: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    chat_name_in_messenger: Optional[str] = None
    chat_url_in_messenger: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )

    user_name_in_messenger: Optional[str] = None
    user_url_in_messenger: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    user_avatar_in_messenger: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    ts_in_messenger: Optional[datetime] = None


@dataclass(order=True)
class EventCommandToSend(LinterFix, AbstractCommand):
    # Перед отправкой мы должны сохранить сообщение и знать его ID
    message_id: Optional[int] = None

    chat_id: Optional[int] = None
    bot_user_id: Optional[int] = None
    lang_code: Optional[str] = None

    inline_buttons: Optional[List[InlineButton]] = None
    inline_buttons_cols: Optional[int] = None


#####

@dataclass(order=True, base_schema=SkipNoneSchema)
class Callback:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    type: CallbackType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(CallbackType, by_value=True)
        }
    )
    id: int
