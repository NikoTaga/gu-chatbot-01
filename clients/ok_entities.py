from dataclasses import field
from typing import ClassVar, List, Optional, Type

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from clients.ok_constants import *


# заставляет отбрасывать все значения None при дампе
# имеет смысл промаркировать все классы, данные из которых планируются к передаче НА удалённый сервер
class SkipNoneSchema(marshmallow.Schema):
    @marshmallow.post_dump
    def remove_none_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


@dataclass(order=True, base_schema=SkipNoneSchema)
class OkSender:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    user_id: str
    name: Optional[str] = None


@dataclass(order=True)
class OkRecipient:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    chat_id: str


@dataclass(order=True, base_schema=SkipNoneSchema)
class OkButton:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    type: OkButtonType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(OkButtonType, by_value=True)
        }
    )
    text: str
    intent: OkButtonIntent = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(OkButtonIntent, by_value=True)
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

    buttons: List[List[OkButton]] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.List(marshmallow.fields.List(
                marshmallow.fields.Nested(OkButton.Schema())),
                allow_none=True,
                # validate=marshmallow.validate.Length(max=3),
            )
        }
    )


@dataclass(order=True, base_schema=SkipNoneSchema)
class OkPayload:
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
class OkAttachment:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    type: AttachmentType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(AttachmentType, by_value=True)
        }
    )
    payload: OkPayload


@dataclass(order=True, base_schema=SkipNoneSchema)
class OkMessage:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    text: Optional[str] = None
    seq: Optional[int] = None
    attachment: Optional[OkAttachment] = None
    attachments: Optional[List[OkAttachment]] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.List(
                marshmallow.fields.Nested(OkAttachment.Schema()),
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
class OkIncomingWebhook:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    webhookType: OkWebhookType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(OkWebhookType, by_value=True)
        }
    )
    sender: OkSender
    recipient: OkRecipient
    timestamp: int
    mid: Optional[str]
    callbackId: Optional[str]
    message: Optional[OkMessage] = None
    type: Optional[OkSystemWebhookType] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(OkSystemWebhookType, by_value=True)
        }
    )
    payload: Optional[str] = None


@dataclass(order=True)
class OkOutgoingMessage:
    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    recipient: OkRecipient
    message: OkMessage
