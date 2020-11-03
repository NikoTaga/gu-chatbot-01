from enum import Enum
from typing import Any, Tuple


class Choice(Enum):
    @classmethod
    def choices(cls) -> Tuple[Tuple[Any, str], ...]:
        return tuple((x.value, x.name.capitalize()) for x in cls)


# ----------------------------
# Bot
# ----------------------------

class BotType(Choice):
    TYPE_JIVOSITE = 10
    TYPE_OK = 11


class ChatType(Choice):
    PRIVATE = 1
    GROUP = 2
    CHANNEL = 3


class MessageStatus(Choice):
    NEW = 1
    SENT = 3
    FAILED = 5
    DELIVERED = 10
    READ = 13
    DELETED = 15


class ContentType(Enum):
    TEXT = 'text'
    IMAGE = 'image'
    FILE = 'file'
    VIDEO = 'video'
    LOCATION = 'location'
    CONTACT = 'contact'
    VOICE = 'voice'

    # Legacy: Special content types
    INLINE = 'inline'
    REMOVE = 'remove'
    MENU_BUTTON = 'menu_button'
    COMMAND = 'command'


class MessageDirection(Choice):
    RECEIVED = 1
    SENT = 2
    SYSTEM = 3


class MessageContentType(Choice):
    TEXT = 1
    IMAGE = 2
    CONTACT = 3
    VOICE = 4
    REMOVE = 5
    COMMAND = 6
    SYSTEM = 7
    FILE = 8
    INLINE = 9


# ----------------------------
# Shop
# ----------------------------

class OrderStatus(Choice):
    NEW = 1
    PENDING_PAYMENT = 2
    PROCESSING = 3
    COMPLETE = 4
    CLOSED = 5
    CANCELED = 6
    ON_HOLD = 7
    PAYMENT_REVIEW = 8


ORDER_STATUS_ENUM = [
    {'id': OrderStatus.NEW.value, 'name': 'New'},
    {'id': OrderStatus.PENDING_PAYMENT.value, 'name': 'Pending payment'},
    {'id': OrderStatus.PROCESSING.value, 'name': 'Processing'},
    {'id': OrderStatus.COMPLETE.value, 'name': 'Complete'},
    {'id': OrderStatus.CLOSED.value, 'name': 'Closed'},
    {'id': OrderStatus.CANCELED.value, 'name': 'Canceled'},
    {'id': OrderStatus.ON_HOLD.value, 'name': 'On hold'},
    {'id': OrderStatus.PAYMENT_REVIEW.value, 'name': 'Payment review'},
]


class GenericTemplateActionType(Enum):
    POSTBACK = 'postback'
    URL = 'url'
