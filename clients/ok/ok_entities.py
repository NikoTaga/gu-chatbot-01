"""Содержит сущности для сериализации данных при обмене с Одноклассниками."""
# todo описать поля классов в докстрингах

from dataclasses import field
from typing import ClassVar, List, Optional, Type

import marshmallow
import marshmallow_enum
from marshmallow_dataclass import dataclass

from clients.ok.ok_constants import (OkButtonType, OkButtonIntent, OkWebhookType, OkSystemWebhookType,
                                     OkPayloadCallType, OkPayloadCallHangupType, OkAttachmentType, OkPrivacyWarningType)
from common.entities import SkipNoneSchema, LinterFix


@dataclass(order=True, base_schema=SkipNoneSchema)
class OkSender:
    """Класс данных для хранения информации о отправителе входящего сообщения OK."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    user_id: str
    name: Optional[str] = None


@dataclass(order=True)
class OkRecipient(LinterFix):
    """Класс данных для хранения информации о получателе входящего сообщения ОК."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    chat_id: str


@dataclass(order=True, base_schema=SkipNoneSchema)
class OkButton(LinterFix):
    """Класс данных для хранения информации о кнопке в сообщении ОК."""

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
class OkButtons(LinterFix):
    """Класс данных для обертывания информации о кнопках в сообщении."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    buttons: List[List[OkButton]] = field(
        # default=None,
        metadata={
            "marshmallow_field": marshmallow.fields.List(marshmallow.fields.List(
                marshmallow.fields.Nested(OkButton.Schema())),
                allow_none=True,
                # validate=marshmallow.validate.Length(max=3),
            )
        }
    )


@dataclass(order=True, base_schema=SkipNoneSchema)
class OkPayload(LinterFix):
    """Класс данных для хранения информации о содержимом приложения в сообщении ОК."""

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
    type: Optional[OkPayloadCallType] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(OkPayloadCallType, by_value=True)
        }
    )
    hangupType: Optional[OkPayloadCallHangupType] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(OkPayloadCallHangupType, by_value=True)
        }
    )
    duration: Optional[int] = None
    keyboard: Optional[OkButtons] = None
    callbackId: Optional[str] = None


@dataclass(order=True)
class OkAttachment(LinterFix):
    """Класс данных для хранения информации о приложении к сообщению ОК."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    type: OkAttachmentType = field(
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(OkAttachmentType, by_value=True)
        }
    )
    payload: OkPayload


@dataclass(order=True, base_schema=SkipNoneSchema)
class OkMessage(LinterFix):
    """Класс данных для хранения информации о сообщении ОК."""

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
    privacyWarning: Optional[OkPrivacyWarningType] = field(
        default=None,
        metadata={
            "marshmallow_field": marshmallow_enum.EnumField(OkPrivacyWarningType, by_value=True)
        }
    )
    reply_to: Optional[str] = None


@dataclass(order=True)
class OkIncomingWebhook:
    """Класс данных для хранения информации о входящем вебхуке от ОК."""

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
class OkOutgoingMessage(LinterFix):
    """Класс данных для хранения информации об исходящем сообщении ОК."""

    Schema: ClassVar[Type[marshmallow.Schema]] = marshmallow.Schema

    recipient: OkRecipient
    message: OkMessage
