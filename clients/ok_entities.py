from dataclasses import field
from typing import ClassVar, List, Optional, Type

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from clients.ok_constants import *


# заставляет отбрасывать все значения None при дампе
class SkipNoneSchema(marshmallow.Schema):
    @marshmallow.post_dump
    def remove_none_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


@dataclass(order=True, base_schema=SkipNoneSchema)
class Sender:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    user_id: str
    name: Optional[str] = None


@dataclass(order=True)
class Recipient:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    chat_id: str


@dataclass(order=True, base_schema=SkipNoneSchema)
class Button:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    type: ButtonType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(ButtonType, by_value=True)
        }
    )
    text: str
    intent: ButtonIntent = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(ButtonIntent, by_value=True)
        }
    )
    payload: Optional[str] = None
    url: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    quick: Optional[bool] = None


@dataclass(order=True, base_schema=SkipNoneSchema)
class OkButtons:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    buttons: List[List[Button]] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.List(marshmallow.fields.List(
                marshmallow.fields.Nested(Button.Schema())),
                allow_none=True,
                # validate=marshmallow.validate.Length(max=3),
            )
        }
    )


@dataclass(order=True, base_schema=SkipNoneSchema)
class Payload:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    id: Optional[str] = None
    token: Optional[str] = None
    url: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    name: Optional[str] = None
    phone: Optional[str] = None
    photoUrl: Optional[str] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.Url(allow_none=True)
        }
    )
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    zoom: Optional[int] = None
    type: Optional[PayloadCallType] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(PayloadCallType, by_value=True)
        }
    )
    hangupType: Optional[PayloadCallHangupType] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(PayloadCallHangupType, by_value=True)
        }
    )
    duration: Optional[int] = None
    keyboard: Optional[OkButtons] = None
    callbackId: Optional[str] = None


@dataclass(order=True)
class Attachment:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    type: AttachmentType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(AttachmentType, by_value=True)
        }
    )
    payload: Payload


@dataclass(order=True, base_schema=SkipNoneSchema)
class Message:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    text: Optional[str] = None
    seq: Optional[int] = None
    attachment: Optional[Attachment] = None
    attachments: Optional[List[Attachment]] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow.fields.Nested(Attachment.Schema()),
                allow_none=True,
                # validate=marshmallow.validate.Length(max=3),
            )
        }
    )
    mid: Optional[str] = None
    privacyWarning: Optional[PrivacyWarningType] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(PrivacyWarningType, by_value=True)
        }
    )
    reply_to: Optional[str] = None


@dataclass(order=True)
class IncomingWebhook:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    webhookType: WebhookType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(WebhookType, by_value=True)
        }
    )
    sender: Sender
    recipient: Recipient
    timestamp: int
    mid: Optional[str]
    callbackId: Optional[str]
    message: Optional[Message] = None
    type: Optional[SystemWebhookType] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(SystemWebhookType, by_value=True)
        }
    )
    payload: Optional[str] = None


@dataclass(order=True)
class OutgoingMessage:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    recipient: Recipient
    message: Message
